from logging import getLogger
from uuid import UUID

from pydantic import BaseModel, Field

from math_rag.application.assistants import KatexCorrectorAssistant, KatexCorrectorRetrierAssistant
from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.base.services import BaseKatexCorrectorService
from math_rag.application.models.assistants.inputs import KatexCorrector as AssistantInput
from math_rag.application.models.assistants.inputs import (
    KatexCorrectorRetrier as RetrierAssistantInput,
)
from math_rag.application.models.assistants.outputs import KatexCorrector as AssistantOutput


logger = getLogger(__name__)


class KatexCorrectorTask(BaseModel):
    index: int
    current_katex: str
    num_retries: int = 0
    error: str | None = None
    history: list[tuple[AssistantInput, AssistantOutput]] = Field(default_factory=list)


class KatexCorrectorService(BaseKatexCorrectorService):
    def __init__(
        self,
        katex_client: BaseKatexClient,
        katex_corrector_assistant: KatexCorrectorAssistant,
        katex_corrector_retrier_assistant: KatexCorrectorRetrierAssistant,
    ):
        self.katex_client = katex_client
        self.katex_corrector_assistant = katex_corrector_assistant
        self.katex_corrector_retrier_assistant = katex_corrector_retrier_assistant

    async def correct(self, katexes: list[str], *, max_num_retries: int) -> list[str]:
        # initialize tasks, one per input, preserving original order via index
        tasks = [
            KatexCorrectorTask(index=i, current_katex=katex) for i, katex in enumerate(katexes)
        ]

        # phase 1: initial validation and katex corrector
        to_validate = [task.current_katex for task in tasks]
        initial_results = await self.katex_client.batch_validate_many(to_validate, batch_size=50)

        # collect tasks that need correction
        input_id_to_task: dict[UUID, KatexCorrectorTask] = {}
        input_id_to_input: dict[UUID, AssistantInput] = {}
        initial_inputs: list[AssistantInput] = []
        invalid_tasks: list[KatexCorrectorTask] = []

        for task, result in zip(tasks, initial_results):
            if not result.valid:
                if result.error is None:
                    raise ValueError()

                task.error = result.error
                ci = AssistantInput(katex=task.current_katex, error=task.error)
                initial_inputs.append(ci)
                input_id_to_task[ci.id] = task
                input_id_to_input[ci.id] = ci
                invalid_tasks.append(task)

            else:
                task.num_retries = 0

        # run the corrector exactly once on all initially invalid katexes
        if initial_inputs:
            outputs = await self.katex_corrector_assistant.concurrent_assist(initial_inputs)

            for output in outputs:
                task = input_id_to_task[output.input_id]
                input = input_id_to_input[output.input_id]
                task.history.append((input, output))
                task.current_katex = output.katex
                task.num_retries = 1

        # phase 2: retry loop with validation and katex retrier corrector
        while invalid_tasks:
            # re-validate what's still invalid
            to_validate = [task.current_katex for task in invalid_tasks]
            results = await self.katex_client.batch_validate_many(to_validate, batch_size=50)

            next_invalid_tasks: list[KatexCorrectorTask] = []
            retrier_inputs: list[RetrierAssistantInput] = []
            retrier_input_id_to_task: dict[UUID, KatexCorrectorTask] = {}
            retrier_input_id_to_input: dict[UUID, RetrierAssistantInput] = {}

            # build retrier inputs for those still failing
            for task, result in zip(invalid_tasks, results):
                if result.valid:
                    continue

                if result.error is None:
                    raise ValueError()

                task.error = result.error

                # assemble every previous (input, output) plus the new one with None output
                history_pairs = [(ci, co) for (ci, co) in task.history]
                ci = AssistantInput(katex=task.current_katex, error=task.error)
                history_pairs.append((ci, None))
                ri = RetrierAssistantInput(pairs=history_pairs)
                retrier_inputs.append(ri)
                retrier_input_id_to_task[ri.id] = task
                retrier_input_id_to_input[ri.id] = ri

                # mark for next round if retries remain
                next_invalid_tasks.append(task)

            if not retrier_inputs:
                break

            # call retrier in one batch
            retrier_outputs = await self.katex_corrector_retrier_assistant.concurrent_assist(
                retrier_inputs
            )

            # apply retrier outputs, bump retries, check max_num_retries
            invalid_tasks: list[KatexCorrectorTask] = []

            for output in retrier_outputs:
                task = retrier_input_id_to_task[output.input_id]
                input = retrier_input_id_to_input[output.input_id]
                task.history.append((input, output))
                task.current_katex = output.katex
                task.num_retries += 1

                if task.num_retries > max_num_retries:
                    raise RuntimeError(f'Max retries reached for KaTeX at index {task.index}')

                invalid_tasks.append(task)

        # return corrected katexes in the original order
        tasks.sort(key=lambda task: task.index)

        return [task.current_katex for task in tasks]

from asyncio import Condition, Lock


class FineTuneJobRunContext:
    condition = Condition()
    lock = Lock()

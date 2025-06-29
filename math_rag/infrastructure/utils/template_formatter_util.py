import re

from math_rag.infrastructure.constants.services import MATH_PLACEHOLDER_PATTERN


class TemplateFormatterUtil:
    @staticmethod
    def format(
        text: str, index_to_arg: dict[int, str], *, omit_wrapper: bool
    ) -> tuple[str, list[int]]:
        """
        Replace each [math_placeholder | int] in the text with
        '[arg | int]' by default or 'arg' if omit_wrapper is True.
        Placeholders without a mapping remain unchanged.
        Returns the fully formatted text.
        """
        placeholder_regex = re.compile(MATH_PLACEHOLDER_PATTERN)
        index_extractor = re.compile(r'\|\s*(\d+)\]')

        result_indexes: list[int] = []
        result_parts: list[str] = []
        last_end = 0

        for match in placeholder_regex.finditer(text):
            start, end = match.span()

            # append text before placeholder
            result_parts.append(text[last_end:start])

            placeholder_text = match.group(0)
            index_match = index_extractor.search(placeholder_text)

            if index_match:
                index = int(index_match.group(1))
                arg = index_to_arg.get(index)
                result_indexes.append(index)

                if arg is None:
                    replacement = placeholder_text

                elif omit_wrapper:
                    replacement = arg

                else:
                    replacement = f'[{arg} | {index}]'

            else:
                replacement = placeholder_text

            result_parts.append(replacement)
            last_end = end

        # append text after last placeholder
        result_parts.append(text[last_end:])

        return str().join(result_parts), result_indexes

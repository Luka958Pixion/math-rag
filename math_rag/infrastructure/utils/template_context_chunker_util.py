import re

from math_rag.infrastructure.constants.services import (
    MATH_PLACEHOLDER_INDEX_PATTERN,
    MATH_PLACEHOLDER_PATTERN,
)


class TemplateContextChunkerUtil:
    @staticmethod
    def chunk(text: str, *, max_context_size: int) -> list[tuple[str, list[int]]]:
        """
        For each math-placeholder in text, return a context substring of up to
        max_context_size characters total (including the placeholder itself),
        without cutting words or placeholders.
        """
        matches = list(re.finditer(MATH_PLACEHOLDER_PATTERN, text))
        placeholder_spans = [(match.start(), match.end()) for match in matches]
        text_length = len(text)
        contexts: list[str] = []

        for start_index, end_index in placeholder_spans:
            placeholder_length = end_index - start_index
            available_context = max_context_size - placeholder_length

            # split context to left and right
            context_left = available_context // 2
            context_right = available_context - context_left

            raw_start = max(0, start_index - context_left)
            raw_end = min(text_length, end_index + context_right)

            # expand to word boundary on the left
            if raw_start > 0 and text[raw_start].isalnum():
                boundary = text.rfind(' ', 0, raw_start)
                raw_start = 0 if boundary == -1 else boundary + 1

            # expand to word boundary on the right
            if raw_end < text_length and text[raw_end].isalnum():
                boundary = text.find(' ', raw_end)
                raw_end = text_length if boundary == -1 else boundary

            # ensure no placeholder is cut
            context_start, context_end = raw_start, raw_end

            for span_start, span_end in placeholder_spans:
                if span_start < context_start < span_end:
                    context_start = span_start

                if span_start < context_end < span_end:
                    context_end = span_end

            contexts.append(text[context_start:context_end])

        # find indexes within each context
        results = []

        for context in contexts:
            matches = re.finditer(MATH_PLACEHOLDER_INDEX_PATTERN, context)
            indexes = []

            for match in matches:
                index = match.group(1)

                if index is None:
                    raise ValueError(f'Match {match} does not have an index')

                indexes.append(int(index))

            results.append((context, indexes))

        return results

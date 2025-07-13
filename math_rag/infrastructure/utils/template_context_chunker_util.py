import re

from math_rag.infrastructure.constants.services import (
    IMAGE_PLACEHOLDER_PATTERN,
    MATH_PLACEHOLDER_PATTERN,
)


class TemplateContextChunkerUtil:
    @staticmethod
    def chunk(text: str, *, max_context_size: int) -> list[str]:
        """
        For each math-placeholder in text, return a context substring of up to
        max_context_size characters total (including the placeholder itself),
        without cutting word, image or math placeholders.
        """
        image_matches = list(re.finditer(IMAGE_PLACEHOLDER_PATTERN, text))
        image_placeholder_spans = [(match.start(), match.end()) for match in image_matches]

        math_matches = list(re.finditer(MATH_PLACEHOLDER_PATTERN, text))
        math_placeholder_spans = [(match.start(), match.end()) for match in math_matches]

        all_placeholder_spans = image_placeholder_spans + math_placeholder_spans

        text_length = len(text)
        contexts: list[str] = []

        for start_index, end_index in math_placeholder_spans:
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

            # ensure no image or math placeholder is cut
            context_start, context_end = raw_start, raw_end

            for span_start, span_end in all_placeholder_spans:
                if span_start < context_start < span_end:
                    context_start = span_start

                if span_start < context_end < span_end:
                    context_end = span_end

            contexts.append(text[context_start:context_end])

        return contexts

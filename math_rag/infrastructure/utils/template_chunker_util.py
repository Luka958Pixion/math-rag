import re

from math_rag.infrastructure.constants.services import MATH_PLACEHOLDER_PATTERN


class TemplateChunkerUtil:
    @staticmethod
    def _parse_placeholders(text: str) -> tuple[list[int], list[int]]:
        """
        Find all [math_placeholder | int] spans and return their start positions and lengths.
        """
        matches = list(re.finditer(MATH_PLACEHOLDER_PATTERN, text))
        positions = [match.start() for match in matches]
        lengths = [match.end() - match.start() for match in matches]

        return positions, lengths

    @staticmethod
    def _find_contiguous_block_ranges(
        positions: list[int], lengths: list[int], max_window_size: int
    ) -> list[tuple[int, int]]:
        """
        Split the sequence of placeholders into blocks where gaps between
        consecutive placeholders do not exceed the window size.
        Returns a list of (start_index, end_index) ranges into the positions/lengths lists.
        """
        blocks: list[tuple[int, int]] = []
        i = 0
        n = len(positions)

        while i < n:
            j = i + 1

            while j < n:
                previous_end = positions[j - 1] + lengths[j - 1]
                gap = positions[j] - previous_end

                if gap > max_window_size:
                    break

                # extend block
                j += 1

            blocks.append((i, j))
            i = j

        return blocks

    @staticmethod
    def _chunk_block(
        block_text: str,
        relative_positions: list[int],
        relative_lengths: list[int],
        max_window_size: int,
    ) -> list[str]:
        """
        Apply the sliding-window chunking logic to a single text block
        with entities at relative positions and lengths.
        """
        chunks: list[str] = []
        i = 0
        j = 0
        n = len(relative_positions)

        # build the first window
        while j < n and relative_positions[j] + relative_lengths[j] <= max_window_size:
            j += 1

        first_chunk_end = relative_positions[j - 1] + relative_lengths[j - 1]
        chunks.append(block_text[:first_chunk_end])

        # slide the window over remaining entities
        for k in range(j, n):
            start_position = relative_positions[k]
            length = relative_lengths[k]

            # drop oldest entities until the new one fits
            while i < k:
                window_origin = relative_positions[i]

                if start_position + length - window_origin <= max_window_size:
                    break

                i += 1

            window_origin = relative_positions[i]
            chunk_end = start_position + length
            chunks.append(block_text[window_origin:chunk_end])

        return chunks

    def chunk(text: str, *, max_window_size: int, max_padding: int) -> list[str]:
        """
        Break text into chunks that each include a sliding window of
        [math_placeholder | int] tokens without exceeding max_window_size.
        Optionally pad each chunk by up to max_padding total characters (split evenly)
        without cutting words or including other placeholders.
        """
        positions, lengths = TemplateChunkerUtil._parse_placeholders(text)
        placeholder_spans = [(pos, pos + length) for pos, length in zip(positions, lengths)]
        block_ranges = TemplateChunkerUtil._find_contiguous_block_ranges(
            positions, lengths, max_window_size
        )
        raw_ranges: list[tuple[int, int]] = []

        for i, j in block_ranges:
            block_start = positions[i]
            block_end = positions[j - 1] + lengths[j - 1]
            rel_positions = [pos - block_start for pos in positions[i:j]]
            rel_lengths = lengths[i:j]
            rel_spans = TemplateChunkerUtil._chunk_block(
                text[block_start:block_end], rel_positions, rel_lengths, max_window_size
            )

            for start_rel, end_rel in rel_spans:
                raw_ranges.append((block_start + start_rel, block_start + end_rel))

        chunks: list[str] = []
        text_len = len(text)

        left_pad = max_padding // 2
        right_pad = max_padding - left_pad

        for chunk_start, chunk_end in raw_ranges:
            if max_padding > 0:
                start = max(0, chunk_start - left_pad)
                end = min(text_len, chunk_end + right_pad)

                if start > 0 and text[start].isalnum():
                    b = text.rfind(' ', 0, start)
                    start = 0 if b < 0 else b + 1

                if end < text_len and text[end].isalnum():
                    b = text.find(' ', end)
                    end = text_len if b < 0 else b

                for span_start, span_end in placeholder_spans:
                    if span_start < chunk_start and span_end > start:
                        start = span_end

                    if span_start < end and span_end > chunk_end:
                        end = span_start

                chunks.append(text[start:end])

            else:
                chunks.append(text[chunk_start:chunk_end])

        return chunks

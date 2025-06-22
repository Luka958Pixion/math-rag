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

    @staticmethod
    def chunk(text: str, *, max_window_size: int) -> list[str]:
        """
        Break text into chunks that each include a sliding window of
        [math_placeholder | int] tokens without exceeding max_window_size.
        """
        positions, lengths = TemplateChunkerUtil._parse_placeholders(text)
        block_ranges = TemplateChunkerUtil._find_contiguous_block_ranges(
            positions, lengths, max_window_size
        )
        chunks: list[str] = []

        for i, j in block_ranges:
            # extract the text slice
            block_start_offset = positions[i]
            block_end_offset = positions[j - 1] + lengths[j - 1]
            block_text = text[block_start_offset:block_end_offset]

            # find relative positions and lengths
            relative_positions = [position - block_start_offset for position in positions[i:j]]
            relative_lengths = lengths[i:j]

            # chunk
            block_chunks = TemplateChunkerUtil._chunk_block(
                block_text, relative_positions, relative_lengths, max_window_size
            )
            chunks.extend(block_chunks)

        return chunks

from itertools import combinations
from uuid import UUID


class GroupPrunerUtil:
    def prune(
        candidates: list[UUID], candidate_pair_to_is_connected: dict[tuple[UUID, UUID], bool]
    ) -> list[UUID]:
        """
        Given a list of UUID candidates and a precomputed connections,
        iteratively remove the single candidate with the fewest connections
        (i.e., is_connected=True links) until the remaining set is fully cohesive
        (every pair returns True).
        If one candidate remains, return an empty list because a group can't
        consists of a single element.
        """
        candidates = candidates.copy()
        visited_states: set[tuple[UUID, ...]] = set()

        while True:
            state = tuple(candidates)

            # detect loop
            if state in visited_states:
                break

            visited_states.add(state)
            n = len(candidates)

            if n < 2:
                break

            # count votes
            vote_counts: dict[UUID, int] = {x: 0 for x in candidates}

            for a, b in combinations(candidates, 2):
                if candidate_pair_to_is_connected.get((a, b), False):
                    vote_counts[a] += 1
                    vote_counts[b] += 1

            # full cohesion check, every candidate must link to all others
            if all(cnt == n - 1 for cnt in vote_counts.values()):
                break

            # remove the first candidate with the fewest connections
            min_count = min(vote_counts.values())
            worst_candidates = [x for x in candidates if vote_counts[x] == min_count]
            candidates.remove(worst_candidates[0])

        return [] if len(candidates) == 1 else candidates

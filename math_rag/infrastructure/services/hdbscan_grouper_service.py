from uuid import UUID

from hdbscan import HDBSCAN
from sklearn.metrics.pairwise import cosine_distances

from math_rag.application.base.services import BaseGrouperService


class HDBSCANGrouperService(BaseGrouperService):
    def disjoint(self, groups: list[list[UUID]]) -> bool:
        return len({u for g in groups for u in g}) == sum(len(g) for g in groups)

    def group(self, ids: list[UUID], embeddings: list[list[float]]) -> list[list[UUID]]:
        if not embeddings:
            return []

        distances = cosine_distances(embeddings)
        hdbscan = HDBSCAN(
            min_cluster_size=2,
            max_cluster_size=50,
            cluster_selection_epsilon=0.0,
            metric='precomputed',
        )
        labels = hdbscan.fit_predict(distances)

        # group IDs by label (skip noise: -1)
        groups: dict[int, list[UUID]] = {}

        for id, label in zip(ids, labels):
            if label == -1:
                continue

            groups.setdefault(label, []).append(id)

        final_groups = [groups[label] for label in sorted(groups)]

        if not self.disjoint(final_groups):
            raise ValueError()

        return final_groups

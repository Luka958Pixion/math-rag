from uuid import UUID

from hdbscan import HDBSCAN


class ClustererUtil:
    def cluster(self, ids: list[UUID], embeddings: list[list[float]]) -> list[list[UUID]]:
        if not embeddings:
            return []

        hdbscan = HDBSCAN(
            min_cluster_size=2,
            max_cluster_size=50,
            cluster_selection_epsilon=0.0,
            metric='cosine',
        )
        labels = hdbscan.fit_predict(embeddings)

        # group IDs by label (skip noise: -1)
        clusters: dict[int, list[UUID]] = {}

        for id, label in zip(ids, labels):
            if label == -1:
                continue

            clusters.setdefault(label, []).append(id)

        return [clusters[label] for label in sorted(clusters)]

import numpy as np
import torch

from sklearn.metrics import f1_score


def make_compute_metrics(pad_id: int):
    """
    Returns a compute_metrics(fn) that masks out pad_id before F1.
    """

    def compute_metrics(
        eval_preds: tuple[np.ndarray | torch.Tensor, np.ndarray | torch.Tensor],
    ) -> dict[str, float]:
        logits, labels = eval_preds

        # ensure logits is a Tensor
        if not isinstance(logits, torch.Tensor):
            logits = torch.tensor(logits)
        preds = logits.argmax(dim=-1).cpu().numpy()

        # ensure labels is a Tensor
        if not isinstance(labels, torch.Tensor):
            labels = torch.tensor(labels)
        labels = labels.cpu().numpy()

        # flatten and mask out Pad‐positions
        preds = preds.flatten()
        labels = labels.flatten()
        mask = labels != pad_id
        preds = preds[mask]
        labels = labels[mask]

        unique_labels = set(labels.tolist())
        f1 = f1_score(
            labels,
            preds,
            average='binary' if len(unique_labels) == 2 else 'weighted',
        )
        return {'f1': f1}

    return compute_metrics

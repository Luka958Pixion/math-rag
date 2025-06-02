import numpy as np
import torch

from sklearn.metrics import f1_score


def compute_metrics(
    eval_preds: tuple[np.ndarray | torch.Tensor, np.ndarray | torch.Tensor],
) -> dict[str, float]:
    """
    Compute F1 for either binary or multiclass classification.
    eval_preds is a tuple (logits, labels) coming from SFTTrainer.evaluate().
    """
    logits, labels = eval_preds

    # ensure logits is a Tensor
    if not isinstance(logits, torch.Tensor):
        logits = torch.tensor(logits)

    preds = logits.argmax(dim=-1).cpu().numpy()

    # ensure labels is a Tensor
    if not isinstance(labels, torch.Tensor):
        labels = torch.tensor(labels)

    labels = labels.cpu().numpy()

    # determine if binary or multiclass
    unique_labels = set(labels.flatten().tolist())
    f1 = f1_score(
        labels.flatten(),
        preds.flatten(),
        average='binary' if len(unique_labels) == 2 else 'weighted',
    )

    return {'f1': f1}

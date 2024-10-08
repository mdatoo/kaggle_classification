"""CutMix batch level PyTorch augmentation."""

# pylint: disable=duplicate-code

from typing import Tuple

import numpy as np
import torch

from .batch_augmentation import BatchAugmentation


class CutMixBatchAugmentation(BatchAugmentation):
    """CutMix batch level PyTorch augmentation.

    See https://arxiv.org/pdf/1905.04899.pdf for details.
    """

    def __init__(self, alpha: float = 1.0, probability: float = 1.0) -> None:
        """Initialise object.

        Args:
            alpha: Beta distribution parameter, influences mixing ratio
            probability: Probability of applying augmentation
        """
        super().__init__(probability)
        self.alpha = alpha

    def always_apply(self, batch: Tuple[torch.Tensor, torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Apply CutMix to batch.
        NB: Applies CutMix to all but the last element in the batch (to minimise additional memory footprint).

        Args:
            batch: Batch to apply CutMix to
        """
        images, targets = batch

        for idx in range(len(images) - 1):
            images, targets = self.mix(images, targets, idx, idx + 1)

        return images, targets

    def mix(
        self, images: torch.Tensor, targets: torch.Tensor, idx_0: int, idx_1: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Mix two image_target pairs together.

        Args:
            images: Collection of images
            targets: Collection of targets
            idx_0: Index of first pair
            idx_1: Index of second pair
        """
        ratio = self.mixing_ratio()

        images[idx_0] = self.mix_images(images[idx_0], images[idx_1], ratio)
        targets[idx_0] = self.mix_targets(targets[idx_0], targets[idx_1], ratio)

        return images, targets

    def mixing_ratio(self) -> float:
        """Get mixing ratio between two images."""
        return np.random.beta(self.alpha, self.alpha)

    def mix_images(self, image_0: torch.Tensor, image_1: torch.Tensor, ratio: float) -> torch.Tensor:
        """Mix two images together.

        Args:
            image_0: First image
            image_1: Second image
            ratio: Mixing ratio to use
        """
        w = int(image_0.shape[2] * np.sqrt(1 - ratio))
        h = int(image_0.shape[1] * np.sqrt(1 - ratio))
        x = np.random.randint(low=0, high=image_0.shape[2] - w)
        y = np.random.randint(low=0, high=image_0.shape[1] - h)

        image_0[:, y : y + h, x : x + w] = image_1[:, y : y + h, x : x + w]
        return image_0

    def mix_targets(self, target_0: torch.Tensor, target_1: torch.Tensor, ratio: float) -> torch.Tensor:
        """Mix two targets together.

        Args:
            target_0: First target
            target_1: Second target
            ratio: Mixing ratio to use
        """
        return target_0 * ratio + target_1 * (1 - ratio)  # type: ignore[return-value]

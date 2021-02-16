# MIT License
#
# Copyright (C) The Adversarial Robustness Toolbox (ART) Authors 2021
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
This module implements EoT of adding Gaussian noise with uniformly sampled standard deviation.
"""
import logging
from typing import Tuple, Union, TYPE_CHECKING

import numpy as np

from art.preprocessing.expectation_over_transformation.natural_corruptions.pytorch import EOTNaturalCorruptionsPyTorch

if TYPE_CHECKING:
    import torch

logger = logging.getLogger(__name__)


class EOTGaussianNoisePyTorch(EOTNaturalCorruptionsPyTorch):
    """
    This module implements EoT of adding Gaussian noise with uniformly sampled standard deviation.
    """

    def __init__(
        self,
        nb_samples: int,
        clip_values: Tuple[float, float],
        std: Union[float, Tuple[float, float]],
        apply_fit: bool = False,
        apply_predict: bool = True,
    ) -> None:
        """
        Create an instance of EOTBrightnessPyTorch.

        :param nb_samples: Number of random samples per input sample.
        :param clip_values: Tuple of float representing minimum and maximum values of input `(min, max)`.
        :param std: Range to sample the standard deviation for the Gaussian distribution. A single float
            is translated to range [0, std]. The applied delta is sampled uniformly from this range for each image.
        :param apply_fit: True if applied during fitting/training.
        :param apply_predict: True if applied during predicting.
        """
        super().__init__(
            apply_fit=apply_fit, apply_predict=apply_predict, nb_samples=nb_samples, clip_values=clip_values
        )

        self.std = std
        self.std_range = (0.0, std)
        self._check_params()

    def _corrupt(self, x: "torch.Tensor", **kwargs) -> "torch.Tensor":
        """
        Internal method implementing the corruption per image by adding Gaussian noise.

        :param x: Input samples.
        :return: Corrupted samples.
        """
        import torch  # lgtm [py/repeated-import]

        std_i = np.random.uniform(low=self.std_range[0], high=self.std_range[1])
        delta_i = torch.normal(mean=torch.zeros_like(x), std=torch.ones_like(x) * std_i)
        return torch.clamp(x + delta_i, min=self.clip_values[0], max=self.clip_values[1])

    def _check_params(self) -> None:

        if not (isinstance(self.std, (int, float)) or isinstance(self.std, tuple)) or (
            isinstance(self.std, tuple)
            and (
                len(self.std) != 2
                or not isinstance(self.std[0], (int, float))
                or not isinstance(self.std[1], (int, float))
                or self.std[0] > self.std[1]
            )
        ):
            raise ValueError("The argument `std` has to be a float or tuple of two float values as (min, max).")

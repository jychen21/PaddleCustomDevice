# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import paddle
import numpy as np
from op_test import OpTest

from paddle.nn import functional as F


def sigmoid_array(x):
    return 1 / (1 + np.exp(-x))


class TestLogLossOp(OpTest):
    def setUp(self):
        self.op_type = "log_loss"
        self.set_device()
        self.python_api = F.log_loss
        samples_num = 100

        x = np.random.random((samples_num, 1)).astype("float32")
        predicted = sigmoid_array(x)
        labels = np.random.randint(0, 2, (samples_num, 1)).astype("float32")
        epsilon = 1e-7
        self.inputs = {
            "Predicted": predicted,
            "Labels": labels,
        }

        self.attrs = {"epsilon": epsilon}
        loss = -labels * np.log(predicted + epsilon) - (1 - labels) * np.log(
            1 - predicted + epsilon
        )
        self.outputs = {"Loss": loss}

    def set_device(self):
        self.__class__.use_custom_device = True
        self.place = paddle.CustomPlace("gcu", 0)

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad(self):
        self.check_grad_with_place(self.place, ["Predicted"], "Loss")


if __name__ == "__main__":
    unittest.main()

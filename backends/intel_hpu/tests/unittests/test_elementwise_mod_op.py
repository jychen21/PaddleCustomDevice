# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function, division

import unittest

import numpy as np
import paddle
import paddle.base as base
from tests.op_test import OpTest, skip_check_grad_ci

paddle.enable_static()

class TestElementwiseModOp(OpTest):
    def setUp(self):
        self.op_type = "elementwise_mod"
        self.set_hpu()
        self.init_dtype()
        self.init_axis()
        self.init_input_output()

        self.inputs = {
            "X": OpTest.np_dtype_to_base_dtype(self.x),
            "Y": OpTest.np_dtype_to_base_dtype(self.y),
        }
        self.outputs = {"Out": self.out}

    def set_hpu(self):
        self.__class__.use_custom_device = True
        self.__class__.no_need_check_grad = True
        self.place = paddle.CustomPlace("intel_hpu", 0)

    def init_input_output(self):
        np.random.seed(1024)
        self.x = np.random.uniform(0, 10000, [10, 10]).astype(self.dtype)
        self.y = np.random.uniform(0, 1000, [10, 10]).astype(self.dtype)
        self.out = np.mod(self.x, self.y)
        
        
    def init_dtype(self):
        self.dtype = np.float32

    def init_axis(self):
        self.axis = -1
        
    def test_check_output(self):
        self.check_output_with_place(self.place)


class TestElementwiseModOp_broadcast(TestElementwiseModOp):
    def init_input_output(self):
        self.x = np.random.uniform(-1000, 1000, [13, 10]).astype(self.dtype)
        self.y = np.random.uniform(-100, 100, [10]).astype(self.dtype)
        self.out = np.fmod(self.y + np.fmod(self.x, self.y), self.y)


if __name__ == "__main__":
    unittest.main()
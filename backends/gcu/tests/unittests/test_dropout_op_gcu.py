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

import numpy as np
import unittest
from tests.op_test import OpTest, skip_check_grad_ci
import paddle
import paddle.base as base

paddle.enable_static()


class TestDropoutOp(OpTest):
    def setUp(self):
        self.set_device()
        self.init_dtype()
        self.init_inputs_shape()
        self.init_attrs()
        self.op_type = "dropout"
        np.random.seed(123)
        self.inputs = {"X": np.random.random(self.shape).astype(self.dtype)}
        self.set_output()
        self.attrs = {
            "dropout_prob": self.dropout_prob,
            "fix_seed": self.fix_seed,
            "is_test": self.is_test,
            "dropout_implementation": self.dropout_implementation,
        }

    def set_device(self):
        self.__class__.use_custom_device = True
        self.place = paddle.CustomPlace("gcu", 0)

    def init_dtype(self):
        self.dtype = np.float32

    def init_inputs_shape(self):
        self.shape = [2000]

    def init_attrs(self):
        self.fix_seed = True
        self.is_test = False
        self.dropout_implementation = "upscale_in_train"

    def set_output(self):
        self.__class__.no_need_check_grad = False
        self.dropout_prob = 0.0
        out = self.inputs["X"]
        mask = np.ones(self.shape).astype("uint8")
        self.outputs = {"Out": out, "Mask": mask}

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        if (
            hasattr(self.__class__, "no_need_check_grad")
            and self.__class__.no_need_check_grad is True
        ):
            return

        self.check_grad_with_place(self.place, ["X"], "Out")


class TestDropoutOp2(TestDropoutOp):
    def init_inputs_shape(self):
        self.shape = [32, 64]

    def init_attrs(self):
        self.fix_seed = True
        self.is_test = False
        self.dropout_implementation = "upscale_in_train"

    def set_output(self):
        self.__class__.no_need_check_grad = False
        self.dropout_prob = 1.0
        out = np.zeros(self.shape).astype(self.dtype)
        mask = np.zeros(self.shape).astype("uint8")
        self.outputs = {"Out": out, "Mask": mask}


class TestDropoutOpWithSeed(TestDropoutOp):
    # the seed is a Tensor
    def setUp(self):
        self.op_type = "dropout"
        self.set_device()
        self.dtype = np.float32
        self.inputs = {
            "X": np.random.random((32, 64)).astype(self.dtype),
            "Seed": np.asarray([125], dtype="int32"),
        }
        self.attrs = {
            "dropout_prob": 0.0,
            "is_test": False,
            "dropout_implementation": "upscale_in_train",
        }
        self.outputs = {
            "Out": self.inputs["X"],
            "Mask": np.ones((32, 64)).astype("uint8"),
        }

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        self.check_grad_with_place(self.place, ["X"], "Out")


@skip_check_grad_ci(reason="For inference, check_grad is not required.")
class TestDropoutOpInference(OpTest):
    # is_test = True
    def setUp(self):
        self.op_type = "dropout"
        self.set_device()
        self.init_dtype()
        self.inputs = {"X": np.random.random((32, 64)).astype(self.dtype)}
        self.attrs = {
            "dropout_prob": 0.35,
            "fix_seed": True,
            "is_test": True,
            "dropout_implementation": "upscale_in_train",
        }
        self.outputs = {"Out": self.inputs["X"]}

    def init_dtype(self):
        self.dtype = np.float32

    def set_device(self):
        self.__class__.use_custom_device = True
        self.place = paddle.CustomPlace("gcu", 0)

    def test_check_output(self):
        self.check_output_with_place(self.place)


@skip_check_grad_ci(reason="For inference, check_grad is not required.")
class TestDropoutOpInference2(TestDropoutOpInference):
    def setUp(self):
        self.op_type = "dropout"
        self.set_device()
        self.init_dtype()
        self.inputs = {"X": np.random.random((32, 64, 3)).astype(self.dtype)}
        self.attrs = {
            "dropout_prob": 0.75,
            "is_test": True,
            "dropout_implementation": "upscale_in_train",
        }
        self.outputs = {"Out": self.inputs["X"]}


class TestDropoutOpWithSeed(TestDropoutOp):
    # the seed is a Tensor
    def setUp(self):
        self.op_type = "dropout"
        self.set_device()
        self.init_dtype()
        self.inputs = {
            "X": np.random.random((32, 64)).astype(self.dtype),
            "Seed": np.asarray([125], dtype="int32"),
        }
        self.attrs = {
            "dropout_prob": 0.0,
            "is_test": False,
            "dropout_implementation": "upscale_in_train",
        }
        self.outputs = {
            "Out": self.inputs["X"],
            "Mask": np.ones((32, 64)).astype("uint8"),
        }


class TestDropoutAPI(unittest.TestCase):
    def setUp(self):
        np.random.seed(123)
        self.places = [base.CPUPlace(), paddle.CustomPlace("gcu", 0)]

    def check_static_result(self, place):
        with base.program_guard(base.Program(), base.Program()):
            input = paddle.static.data(name="input", shape=[40, 40], dtype="float32")
            res1 = paddle.nn.functional.dropout(
                x=input, p=0.0, training=False, mode="upscale_in_train"
            )
            res2 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=0, training=True, mode="upscale_in_train"
            )
            res3 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=0, training=False, mode="upscale_in_train"
            )
            res4 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=[0, 1], training=True, mode="upscale_in_train"
            )
            res5 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=[0, 1], training=False, mode="upscale_in_train"
            )
            res6 = paddle.nn.functional.dropout(
                x=input, p=1.0, training=True, mode="upscale_in_train"
            )
            res7 = paddle.nn.functional.dropout(
                x=input, p=0.0, training=True, mode="upscale_in_train"
            )
            res8 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=(0, 1), training=False, mode="upscale_in_train"
            )
            res9 = paddle.nn.functional.dropout(
                x=input, p=0.0, training=False, mode="downgrade_in_infer"
            )
            res10 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=0, training=True, mode="downgrade_in_infer"
            )
            res11 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=0, training=False, mode="downgrade_in_infer"
            )
            res12 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=[0, 1], training=True, mode="downgrade_in_infer"
            )
            res13 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=[0, 1], training=False, mode="downgrade_in_infer"
            )
            res14 = paddle.nn.functional.dropout(
                x=input, p=1.0, training=True, mode="downscale_in_infer"
            )
            res15 = paddle.nn.functional.dropout(
                x=input, p=0.0, training=True, mode="downgrade_in_infer"
            )
            res16 = paddle.nn.functional.dropout(
                x=input, p=0.0, axis=(0, 1), training=False, mode="downgrade_in_infer"
            )

            in_np = np.random.random([40, 40]).astype("float32")
            res_np = in_np
            res_np2 = np.zeros_like(in_np)

            exe = base.Executor(place)
            res_list = [res1, res2, res3, res4, res5, res7, res8]
            for res in res_list:
                fetches = exe.run(
                    base.default_main_program(),
                    feed={"input": in_np},
                    fetch_list=[res],
                )
                np.testing.assert_allclose(fetches[0], res_np)
            fetches2 = exe.run(
                base.default_main_program(), feed={"input": in_np}, fetch_list=[res6]
            )
            np.testing.assert_allclose(fetches2[0], res_np2)

    def test_static(self):
        for place in self.places:
            self.check_static_result(place=place)


if __name__ == "__main__":
    unittest.main()

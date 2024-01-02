// Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "kernels/common_ops/elementwise_ops.h"
#include "kernels/funcs/gcu_op_runner.h"

namespace custom_kernel {

template <typename T, typename Context>
void AddNKernel(const Context& dev_ctx,
                const std::vector<const phi::DenseTensor*>& x,
                phi::DenseTensor* out) {
  dev_ctx.template Alloc<T>(out);
  if (UseScatterMemory()) {
    PADDLE_GCU_KERNEL_START(dev_ctx, "add_n", add_n);
    int n = static_cast<int>(x.size());
    if (n == 1) {
      TensorCopy(dev_ctx, *x[0], false, out);
      return;
    }

    phi::DenseTensor tensor_x = *(x.at(0));
    phi::DenseTensor tensor_y = *(x.at(1));
    add_compute(static_cast<const phi::CustomContext&>(dev_ctx),
                tensor_x,
                tensor_y,
                out);
    for (size_t i = 2; i < x.size(); i++) {
      tensor_x = *(x.at(i));  // x
      tensor_y = *out;        // y

      phi::DenseTensor tmp_tensor;
      tmp_tensor.Resize(out->dims());
      dev_ctx.template Alloc(&tmp_tensor, out->dtype());
      *out = tmp_tensor;  // new out

      add_compute(static_cast<const phi::CustomContext&>(dev_ctx),
                  tensor_x,
                  tensor_y,
                  out);
    }
    PADDLE_GCU_KERNEL_END("add_n", add_n);
  } else {
    TensorNameMap input_names;
    TensorValueMap inputs;
    std::vector<std::string> names;
    names.reserve(x.size());
    std::vector<phi::DenseTensor*> values;
    values.reserve(x.size());
    for (size_t i = 0; i < x.size(); ++i) {
      names.emplace_back(std::string("x_") + std::to_string(i));
      values.emplace_back(const_cast<DenseTensor*>(x[i]));
    }
    input_names["X"] = names;
    inputs["X"] = values;

    TensorNameMap output_names;
    TensorValueMap outputs;

    output_names["Out"] = {"out"};
    outputs["Out"] = {out};

    GcuRunner(input_names, inputs, output_names, outputs, {}, "sum", dev_ctx);
  }
}

}  // namespace custom_kernel

PD_REGISTER_PLUGIN_KERNEL(add_n,
                          gcu,
                          ALL_LAYOUT,
                          custom_kernel::AddNKernel,
                          float,
                          phi::dtype::float16,
                          double) {}

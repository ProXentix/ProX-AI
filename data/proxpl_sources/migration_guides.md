# ProXPL Migration Guides (Python / C++ / Rust to ProXPL)

## 1. Migrating PyTorch Code to Native ProXPL

### Python (PyTorch):
```python
import torch
import torch.nn as nn

class LinearRegression(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)

    def forward(self, x):
        return self.linear(x)
```

### Equivalent ProXPL Code:
```proxpl
use std::tensor::{Tensor, Device};

pub struct LinearRegression {
    pub weights: Tensor<f32, [512, 10]>,
    pub bias: Tensor<f32, [10]>,
}

impl LinearRegression {
    pub fn new(device: Device) -> Self {
        Self {
            weights: Tensor::randn(0.0, 0.01, device),
            bias: Tensor::zeros(device),
        }
    }

    pub async fn forward(&self, x: &Tensor<f32, [128, 512]>) -> Tensor<f32, [128, 10]> {
        let out = x.matmul(&self.weights).await;
        out.add_bias(&self.bias)
    }
}
```

## 2. Migrating C++ CUDA Kernel Envocations to ProXPL `unsafe` Direct Call

### C++ CUDA Kernel:
```cpp
__global__ void add_kernel(float* a, float* b, float* c, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) c[idx] = a[idx] + b[idx];
}
```

### ProXPL FFI Binding:
```proxpl
extern "CUDA" {
    fn add_kernel(a: *const f32, b: *const f32, c: *mut f32, n: i32);
}

pub fn vector_add(a: &Tensor<f32, [1024]>, b: &Tensor<f32, [1024]>) -> Tensor<f32, [1024]> {
    let mut out = Tensor::zeros(a.device);
    unsafe {
        add_kernel(a.as_ptr(), b.as_ptr(), out.as_mut_ptr(), 1024);
    }
    out
}
```

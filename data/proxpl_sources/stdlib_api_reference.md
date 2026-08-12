# ProXPL Standard Library API Reference (`std`)

## 1. `std::tensor` Module

The `std::tensor` module provides high-throughput tensor operations optimized for CPU (AVX-512, AMX) and GPU (CUDA, ROCm).

```proxpl
pub struct Tensor<T, Shape> {
    pub data_ptr: usize,
    pub shape: Vec<usize>,
    pub strides: Vec<usize>,
    pub device: Device,
}

impl<T, Shape> Tensor<T, Shape> {
    pub fn zeros(device: Device) -> Self;
    pub fn ones(device: Device) -> Self;
    pub fn randn(mean: f32, std: f32, device: Device) -> Self;
    pub async fn matmul(&self, other: &Self) -> Self;
    pub fn reshape<NewShape>(&self) -> Tensor<T, NewShape>;
    pub fn slice(&self, ranges: &[Range]) -> Self;
}
```

## 2. `std::math` Module

Provides activation functions, normalization methods, and specialized loss functions:

- `relu(x: &Tensor) -> Tensor`
- `gelu(x: &Tensor) -> Tensor`
- `silu(x: &Tensor) -> Tensor`
- `softmax(x: &Tensor, dim: usize) -> Tensor`
- `layer_norm(x: &Tensor, eps: f32) -> Tensor`
- `cross_entropy_loss(logits: &Tensor, targets: &Tensor) -> f32`

## 3. `std::sync` & `std::io` Modules

```proxpl
use std::io::{File, Read, Write};

pub async fn read_checkpoint_header(path: &str) -> Result<Vec<u8>, std::io::Error> {
    let mut file = File::open(path).await?;
    let mut buffer = Vec::with_capacity(1024);
    file.read_exact(&mut buffer).await?;
    Ok(buffer)
}
```

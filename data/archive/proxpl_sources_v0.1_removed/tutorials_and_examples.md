# ProXPL Programming Tutorials & Educational Guides

## Tutorial 1: Building a Transformer Attention Block from Scratch

In this tutorial, we implement a multi-head self-attention module in ProXPL with dynamic batching and flash attention integration.

```proxpl
use std::tensor::{Tensor, Device};
use std::math::attention::flash_attention_v2;

pub struct SelfAttention {
    pub hidden_dim: usize,
    pub num_heads: usize,
    pub head_dim: usize,
    pub q_weights: Tensor<f32, [4096, 4096]>,
    pub k_weights: Tensor<f32, [4096, 4096]>,
    pub v_weights: Tensor<f32, [4096, 4096]>,
    pub out_weights: Tensor<f32, [4096, 4096]>,
}

impl SelfAttention {
    pub fn new(device: Device) -> Self {
        Self {
            hidden_dim: 4096,
            num_heads: 32,
            head_dim: 128,
            q_weights: Tensor::randn(0.0, 0.02, device),
            k_weights: Tensor::randn(0.0, 0.02, device),
            v_weights: Tensor::randn(0.0, 0.02, device),
            out_weights: Tensor::randn(0.0, 0.02, device),
        }
    }

    pub async fn forward(&self, x: &Tensor<f32, [1, 2048, 4096]>) -> Tensor<f32, [1, 2048, 4096]> {
        let q = x.matmul(&self.q_weights).await;
        let k = x.matmul(&self.k_weights).await;
        let v = x.matmul(&self.v_weights).await;

        let attn_out = flash_attention_v2(&q, &k, &v, true, 0.0);
        attn_out.matmul(&self.out_weights).await
    }
}
```

## Tutorial 2: Custom Loss Function & Backward Pass

```proxpl
pub fn mean_squared_error(predictions: &Tensor<f32, [512, 10]>, targets: &Tensor<f32, [512, 10]>) -> f32 {
    let diff = predictions.sub(targets);
    let squared = diff.powf(2.0);
    squared.mean()
}
```

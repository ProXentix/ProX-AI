# ProXPL Formal Language Specification v1.0

ProXPL is a native systems and AI programming language engineered for high-throughput, low-latency AI workload execution and compiler-level optimization.

## 1. Lexical Structure & Grammar

### 1.1 Identifiers & Keywords
ProXPL identifiers follow Unicode Standard Annex #31. Keywords include:
`fn`, `let`, `mut`, `struct`, `enum`, `trait`, `impl`, `type`, `async`, `await`, `spawn`, `channel`, `match`, `if`, `else`, `while`, `for`, `in`, `return`, `defer`, `pub`, `use`, `unsafe`, `tensor`.

### 1.2 Primitive Types
- Integers: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `usize`
- Floating Point: `f16`, `bf16`, `f32`, `f64`
- Boolean: `bool` (`true`, `false`)
- Characters & Strings: `char`, `str`, `String`
- Tensor Primitives: `tensor<DType, Shape>` (e.g., `tensor<f32, [32, 512]>`)

## 2. Type System & Memory Management

### 2.1 Ownership & Borrowing
ProXPL enforces linear type ownership with affine borrowing rules:
- Every value has a single owner binding at any given program execution step.
- Shared references `&T` permit concurrent read-only access.
- Exclusive references `&mut T` guarantee single-writer exclusivity without data races.

### 2.2 Tensor Primitives & Zero-Copy Views
Tensors in ProXPL are first-class memory primitives with static or dynamic shape tracking:
```proxpl
pub fn matmul<const M: usize, const K: usize, const N: usize>(
    a: &tensor<f32, [M, K]>,
    b: &tensor<f32, [K, N]>
) -> tensor<f32, [M, N]> {
    let mut out = tensor::zeros::<f32, [M, N]>();
    unsafe {
        proxpl_cuda_matmul(a.as_ptr(), b.as_ptr(), out.as_mut_ptr(), M, K, N);
    }
    out
}
```

## 3. Concurrency & Async Primitives

ProXPL uses lock-free async/await task scheduling built on an M:N work-stealing runtime threadpool.

```proxpl
pub async fn process_pipeline(channel: Receiver<tensor<f32, [128, 2048]>>) {
    while let Some(batch) = channel.recv().await {
        let normalized = layer_norm(&batch, 1e-5).await;
        let logits = forward_pass(&normalized).await;
        publish_output(logits).await;
    }
}
```

## 4. Error Handling & Pattern Matching

Errors in ProXPL use explicit Result enums (`Result<T, E>`) and Option types (`Option<T>`) combined with pattern matching:

```proxpl
pub fn parse_config(raw: &str) -> Result<ModelConfig, ConfigError> {
    match json::parse(raw) {
        Ok(tree) => Ok(ModelConfig::from_tree(tree)?),
        Err(err) => Err(ConfigError::InvalidSyntax(err)),
    }
}
```

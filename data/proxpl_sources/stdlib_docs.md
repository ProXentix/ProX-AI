# ProXPL Standard Library (`std`) Documentation

The ProXPL standard library provides unified interfaces for high-performance memory management, GPU execution, tensor algebra, networking, and asynchronous synchronization.

## `std::tensor`
High-performance N-dimensional array primitives for GPU & CPU hardware backends.

```proxpl
pub struct Tensor<T, Shape> {
    ptr: *mut T,
    shape: Shape,
    strides: Vec<usize>,
    device: Device,
}

impl<T: Numeric, Shape> Tensor<T, Shape> {
    pub fn zeros(device: Device) -> Self { ... }
    pub fn ones(device: Device) -> Self { ... }
    pub fn reshape<NewShape>(self, new_shape: NewShape) -> Tensor<T, NewShape> { ... }
    pub fn transpose(&self, dim0: usize, dim1: usize) -> Self { ... }
    pub fn to_device(&self, device: Device) -> Self { ... }
}
```

## `std::sync::channel`
Lock-free MPMC (Multi-Producer Multi-Consumer) ring buffer channels for asynchronous task passing.

```proxpl
pub fn channel<T>(capacity: usize) -> (Sender<T>, Receiver<T>) {
    let inner = Arc::new(RingBuffer::new(capacity));
    (Sender { inner: inner.clone() }, Receiver { inner })
}
```

## `std::math::attention`
Fused Scaled Dot-Product Attention kernel wrappers optimized for Tensor Core execution.

```proxpl
pub fn flash_attention_v2<T: FloatDType>(
    q: &Tensor<T, [Batch, Heads, SeqLen, Dim]>,
    k: &Tensor<T, [Batch, Heads, SeqLen, Dim]>,
    v: &Tensor<T, [Batch, Heads, SeqLen, Dim]>,
    causal_mask: bool,
    dropout_p: f32,
) -> Tensor<T, [Batch, Heads, SeqLen, Dim]> {
    // Calls optimized kernel backend
}
```

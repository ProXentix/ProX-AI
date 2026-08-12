# ProXPL Type Semantics, Memory Ownership & Safety Rules

## 1. Type System Overview

ProXPL features a statically typed, affine-linear type system with static type inference, const-generics, and specialized zero-overhead tensor types.

### 1.1 Primitive Numerical Types
- **Signed Integers**: `i8`, `i16`, `i32`, `i64`, `i128`, `isize`
- **Unsigned Integers**: `u8`, `u16`, `u32`, `u64`, `u128`, `usize`
- **Floating Point**: `f16`, `bf16`, `f32`, `f64`
- **Boolean**: `bool` (values: `true`, `false`)
- **Characters & Strings**: `char` (32-bit Unicode code point), `str` (borrowed string slice), `String` (heap-allocated UTF-8 string)

```proxpl
let val_i32: i32 = -42;
let val_f16: f16 = 3.14159_f16;
let val_bf16: bf16 = 1.0_bf16;
let is_active: bool = true;
```

### 1.2 Tensor Primitives & Shape Semantics
Tensors are native memory-managed types with compile-time or dynamic shape tracking:

```proxpl
// Static shape matrix
let weights: Tensor<f32, [4096, 4096]> = Tensor::zeros(Device::Cuda(0));

// Dynamic batch dimension
let batch_inputs: Tensor<f32, [Dyn, 512]> = Tensor::empty(Device::Cpu);
```

## 2. Memory Management & Affine Ownership

ProXPL enforces safety without garbage collection through linear type ownership:

1. **Single Owner Rule**: Each value in ProXPL has exactly one binding owner variable. When the owner scope terminates, the resource is automatically deallocated via `drop()`.
2. **Move Semantics**: Assigning or passing an un-copied type transfers ownership. The source variable becomes invalid.

```proxpl
struct DeviceBuffer {
    pub ptr: usize,
    pub bytes: usize,
}

pub fn consume_buffer(buf: DeviceBuffer) {
    println!("Freeing device memory buffer at address {}", buf.ptr);
}

pub fn main() {
    let buf = DeviceBuffer { ptr: 0xDEADBEEF, bytes: 4096 };
    consume_buffer(buf); // Ownership moved here
    // buf is no longer valid after move
}
```

3. **Borrowing Rules**:
   - Multiple read-only shared references `&T` may exist concurrently.
   - At most one mutable reference `&mut T` may exist for a given resource.
   - Mutable and shared references cannot co-exist in the same lexical lifetime window.

```proxpl
pub fn update_bias(bias: &mut Tensor<f32, [512]>, lr: f32) {
    bias.scale_add(-lr);
}
```

## 3. Atomic Primitives & Raw Pointers

For low-level kernel drivers and FFI compatibility, ProXPL exposes raw pointers inside explicit `unsafe` scopes:

```proxpl
use std::sync::atomic::{AtomicU64, Ordering};

pub struct SharedCounter {
    value: AtomicU64,
}

impl SharedCounter {
    pub fn new() -> Self {
        Self { value: AtomicU64::new(0) }
    }

    pub fn increment(&self) -> u64 {
        self.value.fetch_add(1, Ordering::SeqCst)
    }
}
```

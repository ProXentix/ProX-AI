# ProXPL Virtual Machine & Runtime Specification (`prox-vm`)

The ProXPL Virtual Machine (`prox-vm`) is an asynchronous, lock-free runtime optimized for high-density neural tensor execution and zero-overhead memory reuse.

## 1. Runtime Architecture & Memory Pools

`prox-vm` maintains two isolated memory spaces:

1. **Stack Memory Pool**: Fixed-size lock-free stack frame allocator operating at zero garbage-collection overhead.
2. **Device Tensor Pool**: Unified Virtual Memory (UVM) allocator with asynchronous host-to-device zero-copy memory maps.

```proxpl
pub struct RuntimePool {
    host_arena: ArenaAllocator,
    device_pool: CudaMemoryPool,
    active_tasks: AtomicUsize,
}

impl RuntimePool {
    pub fn allocate_tensor<const D: usize>(&self, shape: [usize; D]) -> *mut f32 {
        self.device_pool.alloc_bytes(shape.iter().product::<usize>() * 4)
    }
}
```

## 2. Bytecode Instruction Set

ProXPL bytecode consists of 32-bit fixed-width instruction words:

| Opcode (8-bit) | Register A (8-bit) | Register B (8-bit) | Register C (8-bit) | Description |
| :--- | :--- | :--- | :--- | :--- |
| `0x01 LOAD_CONST` | `dst` | `const_idx` | `0x00` | Load constant into register |
| `0x10 MATMUL` | `dst` | `src_a` | `src_b` | Execute hardware tensor matrix multiply |
| `0x20 SPAWN_ASYNC` | `dst_channel` | `func_ptr` | `arg_reg` | Spawn async task on work-stealing threadpool |
| `0x30 AWAIT_RECV` | `dst` | `channel_reg` | `0x00` | Suspend coroutine until channel message yields |

## 3. Work-Stealing Task Scheduler

The scheduler runs $N$ OS worker threads matching physical CPU cores, each maintaining a lock-free double-ended work queue (deque). When a worker queue empties, it steals task frames from randomized neighbor queues.

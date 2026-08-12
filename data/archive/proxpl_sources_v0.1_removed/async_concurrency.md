# ProXPL Async Concurrency & Work-Stealing Runtime

## 1. Async Task Model & Lightweight Threads

ProXPL uses an M:N task scheduler that multiplexes thousands of lightweight async tasks over a fixed set of worker OS threads.

### 1.1 `async` Functions and Blocks
Functions declared with `async fn` return a state machine implementing the `Future` trait:

```proxpl
use std::async::spawn;
use std::sync::channel;

pub async fn compute_logits(features: Tensor<f32, [64, 512]>) -> Tensor<f32, [64, 1000]> {
    let normalized = features.layer_norm(1e-5).await;
    let projection = Tensor::load_weights("model.weights.bin").await;
    normalized.matmul(&projection).await
}
```

### 1.2 Channel Communication
Inter-task communication is handled via lock-free bounded or unbounded channels:

```proxpl
pub async fn producer_consumer_demo() {
    let (sender, receiver) = channel::bounded::<i32>(100);

    spawn(async move {
        for i in 0..10 {
            sender.send(i).await.unwrap();
        }
    });

    spawn(async move {
        while let Some(val) = receiver.recv().await {
            println!("Received token index: {}", val);
        }
    });
}
```

## 2. Work-Stealing Runtime Architecture

```text
Worker Thread 0          Worker Thread 1          Worker Thread 2
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│ Local Queue  │         │ Local Queue  │         │ Local Queue  │
│ [T1, T2, T3] │         │ [T4, T5]     │         │ [ Empty ]    │
└──────┬───────┘         └──────────────┘         └──────▲───────┘
       │                                                 │ Steal Task
       └─────────────────────────────────────────────────┘
```

The runtime enforces work-stealing when a thread queue becomes empty, maintaining high GPU/CPU compute utilization.

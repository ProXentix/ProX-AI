# ProXPL Language Tutorial & Programming Idioms

Welcome to ProXPL, the high-performance AI systems programming language!

## Tutorial 1: Hello World & Function Declarations

```proxpl
pub fn main() {
    let message: &str = "Hello from ProXPL Systems Language!";
    println!("{}", message);
}
```

## Tutorial 2: Tensor Manipulation & Reshaping

```proxpl
use std::tensor::{Tensor, Device, DType};

pub fn build_embedding_layer(vocab_size: usize, hidden_dim: usize) -> Tensor<f32, [32000, 4096]> {
    let weight = Tensor::random_normal([vocab_size, hidden_dim], 0.0, 0.02, Device::Cuda(0));
    println!("Embedding weight matrix initialized: shape = {:?}", weight.shape());
    weight
}
```

## Tutorial 3: Asynchronous RPC & Task Concurrency

```proxpl
use std::sync::channel;

pub async fn worker_task(id: usize, rx: Receiver<String>) {
    while let Some(job) = rx.recv().await {
        println!("Worker {} processing job: {}", id, job);
    }
}

pub async fn main_async() {
    let (tx, rx) = channel::<String>(100);
    spawn(worker_task(1, rx.clone()));
    spawn(worker_task(2, rx));

    tx.send("Job 1: Compute Logits".to_string()).await;
    tx.send("Job 2: Compute Loss".to_string()).await;
}
```

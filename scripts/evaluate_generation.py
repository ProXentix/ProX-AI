import argparse
import os
import torch
import json
from backend.models.neurix import NeurixTransformer
from backend.tokenizer.tokenizer import ProXTokenizer
from backend.inference.generation import GenerationEngine

PROMPTS = {
    "General": [
        "Explain the process of photosynthesis in simple terms.",
        "Summarize the plot of Romeo and Juliet.",
        "Who was the first president of the United States?",
        "Once upon a time in a faraway land,"
    ],
    "Hindi": [
        "भारत की राजधानी क्या है?",
        "मशीन लर्निंग कैसे काम करता है, कृपया समझाइए।",
        "इस कहानी का सारांश दें: एक कछुआ और खरगोश...",
        "Python programming language के फायदे क्या हैं?"
    ],
    "Programming": [
        "Write a Python function to calculate the Fibonacci sequence.",
        "How do you declare a variable in Rust?",
        "Write a SQL query to find all users over age 30.",
        "Write a C++ class for a linked list node.",
        "Write a simple Go web server.",
        "Create a TypeScript interface for a User object.",
        "Write a JavaScript function to fetch data from an API.",
        "fn main() { // ProXPL code"
    ],
    "Mathematics": [
        "What is the derivative of x^2 + 3x?",
        "Solve for x: 2x + 5 = 15.",
        "If I have 5 apples and eat 2, how many are left?",
        "Prove that the square root of 2 is irrational."
    ],
    "Technical": [
        "Explain the difference between TCP and UDP.",
        "What is a compiler and how does it work?",
        "How does virtual memory work in an operating system?",
        "Explain the concept of database normalization."
    ]
}

def main():
    parser = argparse.ArgumentParser(description="Evaluate Generation Quality")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--tokenizer", type=str, default="./weights/tokenizer/tokenizer.json", help="Path to tokenizer")
    parser.add_argument("--device", type=str, default="cpu", help="Device to run on (cpu, cuda)")
    parser.add_argument("--max_new_tokens", type=int, default=128, help="Max tokens to generate")
    args = parser.parse_args()

    print(f"Loading Tokenizer from {args.tokenizer}")
    tokenizer = ProXTokenizer(tokenizer_path=args.tokenizer, allow_fallback=False)
    
    print(f"Loading Model from {args.checkpoint} onto {args.device}")
    ckpt = torch.load(args.checkpoint, map_location=args.device, weights_only=False)
    
    model_config = ckpt.get("model_config")
    if not model_config:
        raise ValueError("Checkpoint missing model_config")
    
    model = NeurixTransformer(model_config)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    
    engine = GenerationEngine(model, tokenizer, device=args.device)
    
    results = []
    
    print("\n" + "="*50)
    print("STARTING GENERATION EVALUATION")
    print("="*50)

    for category, category_prompts in PROMPTS.items():
        print(f"\n--- {category.upper()} ---")
        for prompt in category_prompts:
            print(f"\nPrompt: '{prompt}'")
            res = engine.generate(
                prompt=prompt,
                max_new_tokens=args.max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                use_kv_cache=True
            )
            print(f"Generation: '{res['text']}'")
            print(f"Latency: {res['latency_seconds']:.2f}s | Tokens/sec: {res['tokens_per_second']:.1f}")
            
            results.append({
                "category": category,
                "prompt": prompt,
                "generation": res['text'],
                "latency_seconds": res['latency_seconds'],
                "tokens_per_second": res['tokens_per_second'],
                "total_tokens": res['total_tokens']
            })
            
    print("\n" + "="*50)
    print("EVALUATION COMPLETE")
    print("="*50 + "\n")
    
if __name__ == "__main__":
    main()

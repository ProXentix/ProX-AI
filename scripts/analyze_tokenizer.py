import argparse
import json
from backend.tokenizer.tokenizer import ProXTokenizer

def analyze_tokenizer(tokenizer_path=None):
    tokenizer = ProXTokenizer(tokenizer_path=tokenizer_path, allow_fallback=False)
    
    samples = {
        "English": "The quick brown fox jumps over the lazy dog. This is a standard test for measuring the vocabulary efficiency of a tokenizer.",
        "Hindi": "यह एक परीक्षण है कि यह टोकनाइज़र हिंदी भाषा को कितनी अच्छी तरह समझता है। मशीन लर्निंग मॉडल के लिए भाषा का प्रतिनिधित्व महत्वपूर्ण है।",
        "Hindi-English": "Machine learning मॉडल के लिए tokenization बहुत important है। इससे performance में सुधार होता है।",
        "Python Code": "def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
        "ProXPL Code": "fn main() {\n    let x: int = 42;\n    print(\"Hello ProX\");\n}",
        "Mathematics": "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2} \\quad \\text{where } n \\in \\mathbb{N}"
    }

    print("\n" + "="*50)
    print("TOKENIZER ANALYSIS REPORT")
    print(f"Vocabulary Size: {tokenizer.vocab_size}")
    print("="*50)
    
    for category, text in samples.items():
        tokens = tokenizer.encode(text)
        num_tokens = len(tokens)
        num_chars = len(text)
        num_words = len(text.split())
        
        chars_per_token = num_chars / max(1, num_tokens)
        tokens_per_word = num_tokens / max(1, num_words)
        
        print(f"\n--- {category} ---")
        print(f"Sample: {text[:60]}...")
        print(f"Tokens: {num_tokens} | Chars: {num_chars} | Words: {num_words}")
        print(f"Efficiency: {chars_per_token:.2f} chars/token | {tokens_per_word:.2f} tokens/word")
        
    print("\n" + "="*50)
    print("RECOMMENDATION:")
    print("If Hindi or Math yields < 2.0 chars/token (meaning high fragmentation),")
    print("consider expanding the vocabulary or training a targeted BPE model.")
    print("Otherwise, 32K is sufficient.")
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokenizer", type=str, default=None)
    args = parser.parse_args()
    analyze_tokenizer(args.tokenizer)

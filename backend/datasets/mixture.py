import random
from typing import Dict, List
from backend.datasets.loader import LocalDatasetLoader

DEFAULT_MIXTURE_WEIGHTS = {
    "general_text": 0.40,
    "programming": 0.25,
    "reasoning": 0.15,
    "proxpl": 0.15,
    "documentation": 0.05
}

class DatasetMixture:
    def __init__(self, category_paths: Dict[str, str], weights: Dict[str, float] = None):
        self.category_paths = category_paths
        self.weights = weights or DEFAULT_MIXTURE_WEIGHTS
        self.categories = list(category_paths.keys())

    def sample_mixed_texts(self, total_samples: int = 1000) -> List[str]:
        mixed_texts = []
        for cat, path in self.category_paths.items():
            loader = LocalDatasetLoader(path)
            texts = loader.load_texts()
            weight = self.weights.get(cat, 0.1)
            num_to_take = max(1, int(total_samples * weight))
            if texts:
                sampled = random.choices(texts, k=num_to_take)
                mixed_texts.extend(sampled)
        random.shuffle(mixed_texts)
        return mixed_texts

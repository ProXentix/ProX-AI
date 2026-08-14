import os
import re
from enum import Enum
from typing import Dict, Any, List

class DataCategory(str, Enum):
    GENERAL_NATURAL_LANGUAGE = "general_natural_language"
    PROGRAMMING_LANGUAGES = "programming_languages"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    MATHEMATICS_REASONING = "mathematics_reasoning"
    HINDI = "hindi"
    OTHER_INDIC = "other_indic"

CANONICAL_CATEGORIES = [c.value for c in DataCategory]

EXTENSION_CATEGORY_MAP = {
    ".py": DataCategory.PROGRAMMING_LANGUAGES,
    ".js": DataCategory.PROGRAMMING_LANGUAGES,
    ".ts": DataCategory.PROGRAMMING_LANGUAGES,
    ".c": DataCategory.PROGRAMMING_LANGUAGES,
    ".cpp": DataCategory.PROGRAMMING_LANGUAGES,
    ".rs": DataCategory.PROGRAMMING_LANGUAGES,
    ".go": DataCategory.PROGRAMMING_LANGUAGES,
    ".java": DataCategory.PROGRAMMING_LANGUAGES,
    ".md": DataCategory.TECHNICAL_DOCUMENTATION,
    ".rst": DataCategory.TECHNICAL_DOCUMENTATION,
    ".tex": DataCategory.MATHEMATICS_REASONING,
    ".json": DataCategory.TECHNICAL_DOCUMENTATION,
    ".yaml": DataCategory.TECHNICAL_DOCUMENTATION,
    ".xml": DataCategory.TECHNICAL_DOCUMENTATION,
    ".txt": DataCategory.GENERAL_NATURAL_LANGUAGE,
}

def classify_document(text: str, file_path: str = "") -> DataCategory:
    """Classifies a document into one of 4 canonical categories based on file extension and syntax heuristics."""
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in EXTENSION_CATEGORY_MAP:
            return EXTENSION_CATEGORY_MAP[ext]

    # Content Heuristics
    if not text:
        return DataCategory.GENERAL_NATURAL_LANGUAGE

    # Indic Language / Hindi Detection
    # Devanagari Unicode Block: U+0900 to U+097F
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    if devanagari_chars > 0:
        # Check if there is a significant presence of Devanagari (handles code-switching too)
        if devanagari_chars / len(text) > 0.02 or devanagari_chars > 15:
            # Distinguish Hindi vs other Devanagari (Marathi, Nepali, etc.) using common Hindi stop words
            hindi_keywords = ["है", "और", "में", "की", "से", "को", "एक", "यह"]
            if any(f" {kw} " in text or text.endswith(kw) or text.endswith(f"{kw}।") for kw in hindi_keywords):
                return DataCategory.HINDI
            return DataCategory.OTHER_INDIC

    # Mathematics & Reasoning heuristics
    if re.search(r"\\(begin|end|frac|sum|int|sqrt|matrix|align)", text) or re.search(r"\b(Theorem|Proof|Lemma|Q\.E\.D\.)\b", text):
        return DataCategory.MATHEMATICS_REASONING

    # Structured technical text heuristics
    stripped = text.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
        return DataCategory.TECHNICAL_DOCUMENTATION

    # Code heuristics
    code_keywords = ["def ", "class ", "function ", "import ", "const ", "return ", "public static void "]
    if any(kw in text for kw in code_keywords):
        return DataCategory.PROGRAMMING_LANGUAGES

    # Markdown / Documentation heuristics
    if text.startswith("#") or "```" in text or "http://" in text or "https://" in text:
        return DataCategory.TECHNICAL_DOCUMENTATION

    return DataCategory.GENERAL_NATURAL_LANGUAGE

def get_category_availability(categorized_docs: Dict[str, List[Any]]) -> Dict[str, str]:
    """Returns availability status ('AVAILABLE' vs 'NOT AVAILABLE') for each canonical category."""
    status = {}
    for cat in CANONICAL_CATEGORIES:
        docs = categorized_docs.get(cat, [])
        status[cat] = "AVAILABLE" if len(docs) > 0 else "NOT AVAILABLE"
    return status

import os
import re
from enum import Enum
from typing import Dict, Any, List

class DataCategory(str, Enum):
    GENERAL_NATURAL_LANGUAGE = "general_natural_language"
    PROGRAMMING_LANGUAGES = "programming_languages"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    PROXPL = "proxpl"
    MATHEMATICS_REASONING = "mathematics_reasoning"
    STRUCTURED_TECHNICAL_TEXT = "structured_technical_text"

CANONICAL_CATEGORIES = [c.value for c in DataCategory]

EXTENSION_CATEGORY_MAP = {
    ".proxpl": DataCategory.PROXPL,
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
    ".json": DataCategory.STRUCTURED_TECHNICAL_TEXT,
    ".yaml": DataCategory.STRUCTURED_TECHNICAL_TEXT,
    ".xml": DataCategory.STRUCTURED_TECHNICAL_TEXT,
    ".txt": DataCategory.GENERAL_NATURAL_LANGUAGE,
}

def classify_document(text: str, file_path: str = "") -> DataCategory:
    """Classifies a document into one of 6 canonical categories based on file extension and syntax heuristics."""
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in EXTENSION_CATEGORY_MAP:
            return EXTENSION_CATEGORY_MAP[ext]

    # Content Heuristics
    if not text:
        return DataCategory.GENERAL_NATURAL_LANGUAGE

    # ProXPL specific heuristics
    if "proxpl" in text.lower() or re.search(r"\bfn\s+main\s*\(\s*\)", text) or re.search(r"\b<proxpl_", text):
        return DataCategory.PROXPL

    # Mathematics & Reasoning heuristics
    if re.search(r"\\(begin|end|frac|sum|int|sqrt|matrix|align)", text) or re.search(r"\b(Theorem|Proof|Lemma|Q\.E\.D\.)\b", text):
        return DataCategory.MATHEMATICS_REASONING

    # Structured technical text heuristics
    stripped = text.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
        return DataCategory.STRUCTURED_TECHNICAL_TEXT

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

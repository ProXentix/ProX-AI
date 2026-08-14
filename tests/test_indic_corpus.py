import pytest
from backend.datasets.quality import validate_hindi_text, detect_indic_language

def test_hindi_language_filtering():
    # Mostly Hindi
    assert validate_hindi_text("यह एक परीक्षण है। This is a test.") == True
    # Mostly English
    assert validate_hindi_text("This is mostly English with just one Hindi word: है") == False
    # No Hindi
    assert validate_hindi_text("This is only English.") == False
    # Only Hindi
    assert validate_hindi_text("यह पूरी तरह से हिंदी में है।") == True

def test_indic_language_detection():
    # Bengali
    assert detect_indic_language("এটি একটি পরীক্ষা") == "bn"
    # Tamil
    assert detect_indic_language("இது ஒரு சோதனை") == "ta"
    # Telugu
    assert detect_indic_language("ఇది ఒక పరీక్ష") == "te"
    # Kannada
    assert detect_indic_language("ಇದು ಒಂದು ಪರೀಕ್ಷೆ") == "kn"
    # Malayalam
    assert detect_indic_language("ഇതൊരു പരീക്ഷണമാണ്") == "ml"
    # Gujarati
    assert detect_indic_language("આ એક કસોટી છે") == "gu"
    # Punjabi
    assert detect_indic_language("ਇਹ ਇੱਕ ਟੈਸਟ ਹੈ") == "pa"
    # Odia
    assert detect_indic_language("ଏହା ଏକ ପରୀକ୍ଷା") == "or"

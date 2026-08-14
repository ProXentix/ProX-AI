import pytest
import torch
from backend.models.config import get_config
from backend.models.neurix import NeurixTransformer
from backend.datasets.categories import classify_document, DataCategory

def test_neurix_1b_config():
    config = get_config("neurix-1b")
    assert config.vocab_size == 32000
    assert config.d_model == 1792
    assert config.n_layers == 24
    assert config.n_heads == 14
    assert config.d_ff == 4800
    assert config.max_seq_len == 4096
    assert config.tie_weights is True

def test_neurix_1b_parameter_count():
    config = get_config("neurix-1b")
    with torch.device('meta'):
        model = NeurixTransformer(config)
    breakdown = model.get_parameter_breakdown()
    
    assert 900_000_000 < breakdown["unique_parameters"] < 1_200_000_000
    assert breakdown["trainable_parameters"] == breakdown["unique_parameters"]

def test_hindi_classification():
    text1 = "यह एक परीक्षण है कि यह टोकनाइज़र हिंदी भाषा को कितनी अच्छी तरह समझता है।"
    assert classify_document(text1) == DataCategory.HINDI
    
    text2 = "Python एक programming language है।"
    assert classify_document(text2) == DataCategory.HINDI

def test_other_indic_classification():
    text_marathi = "माझे नाव रमेश आहे. मी पुण्यात राहतो."
    assert classify_document(text_marathi) == DataCategory.OTHER_INDIC

import pytest
import time
import socket
from typing import Dict, Any, Generator

from backend.datasets.streaming import RobustNetworkStreamer

def test_robust_network_streamer_success():
    streamer = RobustNetworkStreamer(max_retries=3, initial_backoff=0.01)
    
    def mock_generator():
        yield {"text": "doc1"}
        yield {"text": "doc2"}

    results = list(streamer.safe_stream(mock_generator, "TestSuccess"))
    assert len(results) == 2
    assert streamer.retry_stats["NETWORK_RETRY_ATTEMPT"] == 0

def test_robust_network_streamer_transient_retry():
    streamer = RobustNetworkStreamer(max_retries=3, initial_backoff=0.01)
    
    attempts = 0
    def mock_generator():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise socket.error("Mock connection reset")
        yield {"text": "doc1"}

    results = list(streamer.safe_stream(mock_generator, "TestRetry"))
    assert len(results) == 1
    assert attempts == 2
    assert streamer.retry_stats["NETWORK_RETRY_ATTEMPT"] == 1
    assert streamer.retry_stats["NETWORK_RETRY_SUCCESS"] == 1
    assert streamer.retry_stats["SOURCE_FAILED"] == 0

def test_robust_network_streamer_exhaustion():
    streamer = RobustNetworkStreamer(max_retries=2, initial_backoff=0.01)
    
    def mock_generator():
        raise TimeoutError("Mock timeout")

    with pytest.raises(TimeoutError):
        list(streamer.safe_stream(mock_generator, "TestFail"))
    
    assert streamer.retry_stats["NETWORK_RETRY_ATTEMPT"] == 3  # Initial + 2 retries
    assert streamer.retry_stats["NETWORK_RETRY_EXHAUSTED"] == 1
    assert streamer.retry_stats["SOURCE_FAILED"] == 1

def test_robust_network_streamer_unexpected_error():
    streamer = RobustNetworkStreamer(max_retries=3, initial_backoff=0.01)
    
    def mock_generator():
        raise ValueError("Unexpected schema error")

    with pytest.raises(ValueError):
        list(streamer.safe_stream(mock_generator, "TestUnexpected"))
    
    assert streamer.retry_stats["NETWORK_RETRY_ATTEMPT"] == 0
    assert streamer.retry_stats["UNEXPECTED_SOURCE_ERROR"] == 1
    assert streamer.retry_stats["SOURCE_FAILED"] == 1

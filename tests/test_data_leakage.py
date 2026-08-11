from backend.datasets.leakage import DataLeakageChecker

def test_data_leakage_detection():
    train_docs = [
        "Training document A: Introduction to neural networks.",
        "Training document B: PyTorch autograd engine internals.",
    ]
    val_docs_clean = [
        "Validation document C: Quantum computing primitives.",
    ]
    val_docs_leaked = [
        "Training document A: Introduction to neural networks.",  # exact leak
    ]

    checker = DataLeakageChecker()
    report_clean = checker.check_leakage(train_docs, val_docs_clean)
    assert report_clean["is_clean"] is True
    assert report_clean["exact_leak_count"] == 0

    report_leaked = checker.check_leakage(train_docs, val_docs_leaked)
    assert report_leaked["is_clean"] is False
    assert report_leaked["exact_leak_count"] == 1

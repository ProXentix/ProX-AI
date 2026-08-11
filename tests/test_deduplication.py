from backend.datasets.deduplication import DatasetDeduplicator

def test_exact_deduplication():
    docs = [
        "Unique document 1",
        "Unique document 2",
        "Unique document 1",  # exact duplicate
    ]
    dedup = DatasetDeduplicator()
    res = dedup.deduplicate_exact(docs)
    assert res["stats"]["input_documents"] == 3
    assert res["stats"]["remaining_documents"] == 2
    assert res["stats"]["duplicates_removed"] == 1

def test_near_deduplication():
    docs = [
        "The quick brown fox jumps over the lazy dog in the park.",
        "The quick brown fox jumps over the lazy dog in the field.",  # near duplicate
        "Completely different technical document about AI compiler architecture.",
    ]
    dedup = DatasetDeduplicator(near_dup_threshold=0.7)
    res = dedup.deduplicate_near(docs)
    assert res["stats"]["input_documents"] == 3
    assert res["stats"]["remaining_documents"] == 2
    assert res["stats"]["near_duplicates_removed"] == 1

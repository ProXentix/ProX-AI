from backend.models.registry import ModelRegistry, ModelLifecycleState

def test_model_registry_lifecycle_and_capabilities():
    registry = ModelRegistry()
    info_list = registry.get_model_info_list()

    assert len(info_list) == 3
    ids = [m["id"] for m in info_list]
    assert "neurix" in ids
    assert "logix" in ids
    assert "optix" in ids

    for info in info_list:
        assert "status" in info
        assert "capabilities" in info
        caps = info["capabilities"]
        # Registry must not claim unverified capabilities
        assert caps["webSearch"] is False
        assert caps["codeExecution"] is False
        assert caps["reasoning"] is False

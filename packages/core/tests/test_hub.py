"""Readiness of pinned model files, against a real Hugging Face cache layout (no network)."""

import pytest

from mcpbytes_core import hub
from mcpbytes_core.errors import ToolError

REVISION = "a" * 40
COMPONENTS = {"main": {"repository": "org/model", "revision": REVISION, "files": {"weights.safetensors": 10, "cfg/config.json": 2}}}


@pytest.fixture
def cache(tmp_path, monkeypatch):
    import huggingface_hub.constants

    monkeypatch.setattr(huggingface_hub.constants, "HF_HUB_CACHE", str(tmp_path))
    return tmp_path / "models--org--model" / "snapshots" / REVISION


def write(root, name, size):
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_bytes(b"x" * size)


def test_nothing_cached_lists_every_file_and_its_size(cache):
    assert hub.missing(COMPONENTS) == {"main": ["weights.safetensors", "cfg/config.json"]}
    assert hub.pending_bytes(COMPONENTS) == 12
    with pytest.raises(ToolError) as error:
        hub.locate(COMPONENTS, "tool download")
    assert error.value.code == "models_missing" and "tool download" in error.value.hint


def test_an_interrupted_download_is_not_treated_as_ready(cache):
    write(cache, "weights.safetensors", 4)
    write(cache, "cfg/config.json", 2)
    assert hub.missing(COMPONENTS) == {"main": ["weights.safetensors"]}


def test_complete_files_resolve_offline_to_the_pinned_snapshot(cache):
    write(cache, "weights.safetensors", 10)
    write(cache, "cfg/config.json", 2)
    assert hub.missing(COMPONENTS) == {}
    assert hub.locate(COMPONENTS, "tool download") == {"main": cache}

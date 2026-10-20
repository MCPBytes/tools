"""Model files pinned to a Hugging Face commit, downloaded on demand into the standard HF cache.

Nothing is bundled: weights come from their publishers under their own licences. A component is
{"repository", "revision" (a commit sha, never a branch), "files": {path: bytes}}; the sizes catch
interrupted or replaced downloads without hashing gigabytes on every start. HF_HOME, HF_ENDPOINT,
HF_TOKEN and HF_HUB_OFFLINE keep their usual meaning.
"""

from pathlib import Path

from .errors import ToolError


def _snapshot(spec, offline):
    from huggingface_hub import snapshot_download

    return Path(snapshot_download(spec["repository"], revision=spec["revision"], allow_patterns=list(spec["files"]),
                                  local_files_only=offline))


def _absent(root, spec):
    return [name for name, size in spec["files"].items() if not ((root / name).is_file() and (root / name).stat().st_size == size)]


def missing(components):
    """{component: [file, ...]} of files not yet in the cache (or of the wrong size); empty when ready."""
    from huggingface_hub.errors import LocalEntryNotFoundError

    result = {}
    for name, spec in components.items():
        try:
            absent = _absent(_snapshot(spec, True), spec)
        except LocalEntryNotFoundError:
            absent = list(spec["files"])
        if absent:
            result[name] = absent
    return result


def pending_bytes(components):
    return sum(components[name]["files"][file] for name, files in missing(components).items() for file in files)


def fetch(components):
    """Download whatever is missing (resumable) and return {component: snapshot folder}."""
    roots = {}
    for name, spec in components.items():
        roots[name] = root = _snapshot(spec, False)
        if absent := _absent(root, spec):
            raise ToolError("download_incomplete", f"{spec['repository']}: {', '.join(absent)} did not download completely",
                            "run the download again; it resumes")
    return roots


def locate(components, command):
    """{component: snapshot folder} without network access; `command` is what the user runs to download."""
    if gone := missing(components):
        raise ToolError("models_missing", f"model files are not downloaded yet ({pending_bytes(components) / 1e9:.1f} GB)",
                        f"run `{command}` once; files: {', '.join(f'{c}/{f}' for c, fs in gone.items() for f in fs)}")
    return {name: _snapshot(spec, True) for name, spec in components.items()}

import hashlib
import secrets

from .errors import ToolError


def require_cuda():
    """torch, after proving a CUDA device can run this build's kernels (a driver or wheel mismatch fails here, not mid-job)."""
    import torch

    if not torch.cuda.is_available():
        raise ToolError("gpu_unavailable", "this PyTorch installation cannot use a CUDA GPU",
                        "PyTorch from PyPI is CPU-only on Windows: reinstall with `uvx --torch-backend=auto ...`, or use --cloud"
                        if torch.version.cuda is None else "check the NVIDIA driver with nvidia-smi, or use --cloud")
    try:
        (torch.ones(1, device="cuda") + 1).cpu()
    except RuntimeError as e:
        raise ToolError("gpu_unsupported", f"{torch.cuda.get_device_name()} cannot run this PyTorch build: {e}", "or use --cloud") from None
    return torch


def job_seed(seed=None):
    return secrets.randbits(32) if seed is None else seed


def stage_seed(seed, stage_id):
    """Per-stage seed derived exactly as the hosted API does, so a job seed means the same locally and in the cloud."""
    return int(hashlib.sha256(f"{seed}:{stage_id}".encode()).hexdigest()[:8], 16)

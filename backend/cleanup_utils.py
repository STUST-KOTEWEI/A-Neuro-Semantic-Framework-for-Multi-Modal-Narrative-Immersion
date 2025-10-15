"""
backend.cleanup_utils

Reusable utilities to clear AI-related caches and resources:
- Stop running Ollama models
- (macOS) Restart Ollama background service
- Clear PyTorch CUDA/MPS caches if PyTorch is installed

These functions are safe to call even if the underlying tools are missing.
"""
from __future__ import annotations

from typing import Any, Dict, List
import os
import platform
import subprocess
import gc


def stop_ollama_models() -> Dict[str, Any]:
    out: Dict[str, Any] = {"stopped": [], "errors": []}
    try:
        ps = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        if ps.returncode != 0:
            if ps.stderr:
                out["errors"].append(ps.stderr.strip())
            return out
        lines = [l.strip() for l in ps.stdout.splitlines() if l.strip()]
        names: List[str] = []
        for line in lines[1:]:
            parts = line.split()
            if parts:
                names.append(parts[0])
        for name in names:
            res = subprocess.run(["ollama", "stop", name], capture_output=True, text=True)
            if res.returncode == 0:
                out["stopped"].append(name)
            elif res.stderr:
                out["errors"].append(res.stderr.strip())
    except FileNotFoundError:
        out["errors"].append("ollama CLI not found")
    except Exception as e:  # pragma: no cover
        out["errors"].append(str(e))
    return out


def restart_ollama_service_if_macos() -> Dict[str, Any]:
    out: Dict[str, Any] = {"restarted": False, "error": None}
    if platform.system().lower() != "darwin":
        return out
    try:
        uid = os.getuid()
        svc = f"gui/{uid}/com.ollama.ollama"
        _ = subprocess.run(["launchctl", "kickstart", "-k", svc], capture_output=True, text=True)
        out["restarted"] = True
    except Exception as e:  # pragma: no cover
        out["error"] = str(e)
    return out


def clear_torch_cache() -> Dict[str, Any]:
    from importlib.util import find_spec

    out: Dict[str, Any] = {"available": False, "cleared": False, "backend": None, "messages": []}
    try:
        spec = find_spec("torch")
        if spec is None:
            out["available"] = False
            return out
        import torch  # type: ignore
        out["available"] = True
        gc.collect()
        # CUDA
        try:
            if hasattr(torch, "cuda") and callable(getattr(torch.cuda, "is_available", None)) and torch.cuda.is_available():
                if hasattr(torch.cuda, "empty_cache"):
                    torch.cuda.empty_cache()
                if hasattr(torch.cuda, "ipc_collect"):
                    torch.cuda.ipc_collect()
                out["cleared"] = True
                out["backend"] = "cuda"
        except Exception as e:  # pragma: no cover
            out["messages"].append(str(e))
        # MPS (macOS Metal)
        try:
            if hasattr(torch, "mps") and hasattr(torch.mps, "is_available") and torch.mps.is_available():
                if hasattr(torch.mps, "empty_cache"):
                    torch.mps.empty_cache()
                out["cleared"] = True
                if out["backend"] is None:
                    out["backend"] = "mps"
        except Exception as e:  # pragma: no cover
            out["messages"].append(str(e))
    except Exception as e:  # pragma: no cover
        out["messages"].append(str(e))
    return out


def clear_all(restart_ollama: bool = True, clear_torch: bool = True) -> Dict[str, Any]:
    """Run all cleanup steps and return a report."""
    report: Dict[str, Any] = {}
    report["ollama"] = stop_ollama_models()
    report["ollama_service"] = restart_ollama_service_if_macos() if restart_ollama else {"restarted": False}
    report["torch"] = clear_torch_cache() if clear_torch else {"skipped": True}
    return report

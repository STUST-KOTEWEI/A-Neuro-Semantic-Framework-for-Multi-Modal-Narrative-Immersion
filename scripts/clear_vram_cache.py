#!/usr/bin/env python3
"""
clear_vram_cache.py

One-click VRAM/GPU cache cleanup for development.
- Stops any running Ollama models
- (macOS) Restarts Ollama background service
- If PyTorch is available, runs gc.collect() and empties CUDA/MPS caches

Usage:
  python scripts/clear_vram_cache.py

Note: This script is safe to run even if some tools are not present; it will skip gracefully.
"""
from __future__ import annotations

import os
import sys
import subprocess
import platform
import gc
from typing import Any, Dict, List


def stop_ollama_models() -> Dict[str, Any]:
    out: Dict[str, Any] = {"stopped": [], "errors": []}
    try:
        ps = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        if ps.returncode != 0:
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
            else:
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
    out: Dict[str, Any] = {"available": False, "cleared": False, "backend": None, "messages": []}
    try:
        from importlib.util import find_spec
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


def main() -> int:
    report: Dict[str, Any] = {}
    report["ollama"] = stop_ollama_models()
    report["ollama_service"] = restart_ollama_service_if_macos()
    report["torch"] = clear_torch_cache()

    print("VRAM cache cleanup report:\n")
    for k, v in report.items():
        print(f"- {k}: {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

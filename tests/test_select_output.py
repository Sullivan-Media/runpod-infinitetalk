"""Self-check for handler.select_output_video (no framework).

Reproduces the (15) log bug: multi-window jobs emit a short _00001.mp4 and a
full _00002-audio.mp4; the handler must return the full one.

Run: python tests/test_select_output.py
"""
import os
import sys
import types
import tempfile

# Stub heavy third-party deps so handler.py imports without them installed.
for name in ("runpod", "websocket", "librosa"):
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules["runpod"].serverless = types.SimpleNamespace(start=lambda *a, **k: None)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from handler import select_output_video


def _write(path, nbytes):
    with open(path, "wb") as f:
        f.write(b"\0" * nbytes)
    return path


def demo():
    with tempfile.TemporaryDirectory() as d:
        short = _write(os.path.join(d, "WanVideo_00001.mp4"), 336094)
        full = _write(os.path.join(d, "WanVideo_00002-audio.mp4"), 1122023)

        # Multi-window: prefer the -audio muxed file even if listed second/larger.
        videos = {"328": [short], "131": [full]}
        assert select_output_video(videos) == full, "must return -audio full clip"

        # No -audio present: fall back to largest (=longest) file.
        big = _write(os.path.join(d, "WanVideo_00002.mp4"), 999999)
        assert select_output_video({"a": [short], "b": [big]}) == big, "largest wins"

        # Single-window: only one file → return it.
        assert select_output_video({"131": [short]}) == short

        # Nothing / missing paths → None.
        assert select_output_video({}) is None
        assert select_output_video({"x": ["/no/such.mp4"]}) is None

    print("ok")


if __name__ == "__main__":
    demo()

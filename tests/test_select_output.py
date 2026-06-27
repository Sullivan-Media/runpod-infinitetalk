"""Self-check for handler.select_output_video — the output-node picker that was
returning the 81-frame silent base (node 328) instead of the full audio-muxed
talking video (node 131). Runs without GPU/runpod/librosa via lightweight stubs."""
import os
import sys
import types
import importlib.util

# Stub runtime-only deps so handler.py imports in a bare env.
for _name in ("runpod", "librosa"):
    sys.modules.setdefault(_name, types.ModuleType(_name))

_HANDLER = os.path.join(os.path.dirname(__file__), "..", "handler.py")
_spec = importlib.util.spec_from_file_location("handler", _HANDLER)
handler = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(handler)
select_output_video = handler.select_output_video


def test_prefers_audio_muxed_output():
    # Mirrors the real ComfyUI output order: [293 empty, 328 silent, 131 audio].
    videos = {
        "293": [],
        "328": ["/ComfyUI/temp/WanVideo2_1_SkyReelsV3_A2V_00001.mp4"],
        "131": ["/ComfyUI/temp/WanVideo2_1_SkyReelsV3_A2V_00002-audio.mp4"],
    }
    assert select_output_video(videos).endswith("00002-audio.mp4")


def test_falls_back_to_first_non_empty():
    assert select_output_video({"293": [], "328": ["/t/x.mp4"]}).endswith("x.mp4")


def test_none_when_all_empty():
    assert select_output_video({"293": [], "328": []}) is None


if __name__ == "__main__":
    test_prefers_audio_muxed_output()
    test_falls_back_to_first_non_empty()
    test_none_when_all_empty()
    print("ok")

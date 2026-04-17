"""Audio backends with auto-detection."""
import os
import subprocess

from .base import AudioBackend
from .pipewire import PipeWireBackend
from .pulseaudio import PulseAudioBackend
from .alsa import ALSABackend


def detect_backend() -> tuple[AudioBackend, str]:
    """Detect and return the active audio backend.

    Returns:
        Tuple of (backend instance, backend name)
    """
    # Check for PipeWire first (most modern)
    if os.path.exists('/run/user/1000/pipewire-0') or os.path.exists('/var/run/user/1000/pipewire-0'):
        try:
            subprocess.run(['wpctl', '--version'], capture_output=True, timeout=5)
            return PipeWireBackend(), "PipeWire"
        except:
            pass

    # Check for PulseAudio
    try:
        subprocess.run(['pactl', '--version'], capture_output=True, timeout=5)
        return PulseAudioBackend(), "PulseAudio"
    except:
        pass

    # Fallback to ALSA
    try:
        subprocess.run(['amixer', '--version'], capture_output=True, timeout=5)
        return ALSABackend(), "ALSA"
    except:
        pass

    return None, None  # type: ignore


__all__ = ['AudioBackend', 'PipeWireBackend', 'PulseAudioBackend', 'ALSABackend', 'detect_backend']
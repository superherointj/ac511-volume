"""PulseAudio backend using pactl."""
import re
import subprocess

from .base import AudioBackend


class PulseAudioBackend(AudioBackend):
    """PulseAudio backend using pactl."""

    def find_sink(self):
        """Find PulseAudio sink by name."""
        try:
            result = subprocess.run(
                ['pactl', 'list', 'short', 'sinks'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n'):
                if 'AC511' in line or 'SoundBar' in line or 'Sound Bar' in line:
                    parts = line.split()
                    if parts:
                        return parts[0]
        except Exception:
            pass
        return None

    def get_volume(self, sink_id):
        try:
            result = subprocess.run(
                ['pactl', 'get-sink-volume', sink_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                match = re.search(r'(\d+)%', result.stdout)
                if match:
                    return int(match.group(1)) / 100.0
        except:
            pass
        return 0.5

    def set_volume(self, sink_id, volume):
        volume = max(0, min(100, int(volume * 100)))
        subprocess.run(
            ['pactl', 'set-sink-volume', sink_id, f"{volume}%"],
            timeout=5
        )
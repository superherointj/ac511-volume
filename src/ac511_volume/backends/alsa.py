"""ALSA backend using amixer."""
import re
import subprocess

from .base import AudioBackend


class ALSABackend(AudioBackend):
    """ALSA backend using amixer."""

    def __init__(self):
        self.card_num = None

    def find_sink(self):
        """Find ALSA card number for Dell AC511."""
        try:
            result = subprocess.run(
                ['aplay', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n'):
                if 'Dell AC511' in line or 'SoundBar' in line:
                    match = re.search(r'card (\d+):', line)
                    if match:
                        self.card_num = match.group(1)
                        return f"hw:{self.card_num}"
        except Exception:
            pass
        return None

    def get_volume(self, sink_id):
        try:
            result = subprocess.run(
                ['amixer', '-D', sink_id, 'sget', 'PCM'],
                capture_output=True,
                text=True,
                timeout=5
            )
            match = re.search(r'(\d+)%', result.stdout)
            if match:
                return int(match.group(1)) / 100.0
        except:
            pass
        return 0.5

    def set_volume(self, sink_id, volume):
        volume = max(0, min(100, int(volume * 100)))
        subprocess.run(
            ['amixer', '-D', sink_id, 'sset', 'PCM', f'{volume}%'],
            timeout=5
        )
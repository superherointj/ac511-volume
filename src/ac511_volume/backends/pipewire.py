"""PipeWire backend using wpctl."""
import re
import subprocess

from .base import AudioBackend


class PipeWireBackend(AudioBackend):
    """PipeWire/WirePlumber backend using wpctl."""

    def find_sink(self):
        """Find the PipeWire sink ID for Dell AC511 SoundBar."""
        try:
            result = subprocess.run(
                ['wpctl', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n'):
                if 'Sound Bar' in line and ('Analog' in line or 'Stereo' in line):
                    match = re.search(r'(\d+)\.\s+.*Sound Bar', line)
                    if match:
                        return int(match.group(1))
        except Exception:
            pass
        return None

    def get_volume(self, sink_id):
        try:
            result = subprocess.run(
                ['wpctl', 'get-volume', str(sink_id)],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and 'Volume:' in result.stdout:
                vol_str = result.stdout.strip().split(':')[1].strip()
                if '%' in vol_str:
                    return float(vol_str.rstrip('%')) / 100.0
                return float(vol_str)
        except:
            pass
        return 0.5

    def set_volume(self, sink_id, volume):
        volume = max(0.0, min(1.0, volume))
        subprocess.run(
            ['wpctl', 'set-volume', str(sink_id), f"{volume:.2f}"],
            timeout=5
        )
"""Audio backend base class."""
from abc import ABC, abstractmethod
from typing import Any, Optional


class AudioBackend(ABC):
    """Base class for audio backends."""

    @abstractmethod
    def find_sink(self) -> Optional[Any]:
        """Find the audio sink for Dell AC511. Returns sink ID or None."""
        pass

    @abstractmethod
    def get_volume(self, sink_id: Any) -> float:
        """Get current volume (0.0 to 1.0)."""
        pass

    @abstractmethod
    def set_volume(self, sink_id: Any, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        pass
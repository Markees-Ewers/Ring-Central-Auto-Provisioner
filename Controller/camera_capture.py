"""Camera frame acquisition.

Author: Markees Ewers
Opens a camera, configure its capture settings, return frames,
and release the camera resource.
"""
from __future__ import annotations

from typing import Any

import cv2


class CameraCapture:
    """Owns the camera resource and returns the latest frame on demand."""

    def __init__(self, camera_index: int) -> None:
        self.camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            self.camera.release()
            self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            raise RuntimeError(f"Could not open camera {camera_index}.")
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def read(self) -> Any:
        """Return the next camera frame."""
        ok, frame = self.camera.read()
        if not ok:
            raise RuntimeError("The camera stopped returning frames.")
        return frame

    def close(self) -> None:
        """Release the camera."""
        self.camera.release()

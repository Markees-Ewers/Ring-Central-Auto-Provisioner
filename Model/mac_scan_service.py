"""Single-image MAC barcode and text scanning.

Author: Markees Ewers
Responsibility: Extract and validate a MAC address from a captured image using
OCR and image preprocessing.
"""

from __future__ import annotations

import re
from pathlib import Path
from threading import Event
from typing import Any

import cv2
import pytesseract

from Model.mac_parser import apply_mac_prefix, parse_mac

OCR_CORRECTIONS = str.maketrans({"O": "0", "Q": "0", "I": "1", "L": "1", "S": "5", "Z": "2"})
OCR_CANDIDATE_PATTERN = re.compile(r"[0-9A-Z][0-9A-Z\s:.-]{8,24}[0-9A-Z]", re.IGNORECASE)
COMPACT_MAC_PATTERN = re.compile(r"(?<![0-9A-Z])[0-9A-Z]{12}(?![0-9A-Z])", re.IGNORECASE)
TESSERACT_PATHS = (
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
)


def configure_tesseract() -> None:
    """Use the standard Windows installation when it is not on PATH."""
    if Path(pytesseract.pytesseract.tesseract_cmd).name.lower() not in {
        "tesseract", "tesseract.exe"
    }:
        return
    for path in TESSERACT_PATHS:
        if path.exists():
            pytesseract.pytesseract.tesseract_cmd = str(path)
            return


class MacScanService:
    """Find one valid MAC from visible text in a captured label image."""

    def scan(
        self,
        frame: Any,
        cancel_event: Event | None = None,
        mac_prefix: str | None = None,
    ) -> str | None:
        """Return a normalized MAC using OCR only."""
        height, width = frame.shape[:2]
        left, top = int(width * 0.02), int(height * 0.04)
        right, bottom = int(width * 0.98), int(height * 0.96)
        label = frame[top:bottom, left:right]

        configure_tesseract()
        try:
            for image in self._ocr_regions(label):
                if cancel_event is not None and cancel_event.is_set():
                    return None
                for psm in (6, 7, 11, 13):
                    if cancel_event is not None and cancel_event.is_set():
                        return None
                    text = pytesseract.image_to_string(image, config=f"--psm {psm}")
                    mac = self._find_mac(text, mac_prefix)
                    if mac:
                        return mac
        except pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError("Tesseract OCR is not installed.") from exc
        return None

    @staticmethod
    def _preprocessed_images(region: Any) -> list[Any]:
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if len(region.shape) == 3 else region
        enlarged = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        normalized = cv2.normalize(enlarged, None, 0, 255, cv2.NORM_MINMAX)
        threshold = cv2.threshold(
            normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]
        adaptive = cv2.adaptiveThreshold(
            normalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 11,
        )
        return [region, enlarged, normalized, threshold, adaptive]

    @classmethod
    def _find_mac(cls, text: str, mac_prefix: str | None = None) -> str | None:
        upper_text = text.upper()
        if mac_prefix:
            for token in COMPACT_MAC_PATTERN.findall(upper_text):
                mac = cls._parse_candidate(token, mac_prefix)
                if mac:
                    return mac
        candidates = OCR_CANDIDATE_PATTERN.findall(upper_text)
        candidates.extend(
            line for line in upper_text.splitlines() if line.strip()
        )
        for token in candidates:
            cleaned = re.sub(r"[^0-9A-Z]", "", token).translate(OCR_CORRECTIONS)
            starts = range(0, max(1, len(cleaned) - 11))
            if mac_prefix:
                starts = reversed(list(starts))
            for start in starts:
                mac = cls._parse_candidate(cleaned[start:start + 12], mac_prefix)
                if mac:
                    return mac
        return None

    @staticmethod
    def _parse_candidate(value: str, mac_prefix: str | None = None) -> str | None:
        candidate = re.sub(r"[^0-9A-Z]", "", value.upper()).translate(OCR_CORRECTIONS)
        if len(candidate) != 12:
            return None
        if mac_prefix:
            candidate = mac_prefix.replace(":", "").replace("-", "") + candidate[6:]
        return apply_mac_prefix(candidate, None)

    @staticmethod
    def _ocr_regions(label: Any) -> list[Any]:
        height = label.shape[0]
        regions = [
            label,
            label[int(height * 0.30):int(height * 0.85)],
            label[int(height * 0.45):int(height * 0.78)],
            label[int(height * 0.55):int(height * 0.90)],
            label[int(height * 0.35):int(height * 0.70)],
        ]
        return [image for region in regions for image in MacScanService._preprocessed_images(region)]

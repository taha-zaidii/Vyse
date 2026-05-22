"""Eye-Aspect-Ratio (EAR) based drowsiness via MediaPipe Face Mesh.

EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)  (Soukupová & Čech 2016)
Threshold default 0.25; sustained drop ≥2s → drowsiness signal.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# MediaPipe Face Mesh landmark indices for the eye corners.
# Order matches the EAR formula above (P1..P6 per eye).
LEFT_EYE_IDX = (33, 160, 158, 133, 153, 144)
RIGHT_EYE_IDX = (362, 385, 387, 263, 373, 380)

DEFAULT_EAR_THRESHOLD = 0.25


@dataclass(slots=True)
class EARResult:
    left_ear: float
    right_ear: float
    avg_ear: float
    landmarks_present: bool


def _euclidean(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def _ear_for(landmarks: np.ndarray, idxs: tuple[int, ...]) -> float:
    p1, p2, p3, p4, p5, p6 = (landmarks[i] for i in idxs)
    vertical = _euclidean(p2, p6) + _euclidean(p3, p5)
    horizontal = _euclidean(p1, p4)
    if horizontal < 1e-6:
        return 0.0
    return vertical / (2.0 * horizontal)


class DrowsinessDetector:
    """One detector per pipeline. Holds a MediaPipe FaceMesh instance internally."""

    def __init__(self, ear_threshold: float = DEFAULT_EAR_THRESHOLD):
        import mediapipe as mp  # type: ignore[import-untyped]

        self.ear_threshold = ear_threshold
        self._mp = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=4,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def infer(self, frame_rgb: np.ndarray) -> list[EARResult]:
        """Process an RGB frame, return one EARResult per detected face."""
        h, w = frame_rgb.shape[:2]
        results = self._mp.process(frame_rgb)
        if not results.multi_face_landmarks:
            return []

        out: list[EARResult] = []
        for face in results.multi_face_landmarks:
            lm_xy = np.array([(p.x * w, p.y * h) for p in face.landmark])
            left = _ear_for(lm_xy, LEFT_EYE_IDX)
            right = _ear_for(lm_xy, RIGHT_EYE_IDX)
            avg = (left + right) / 2.0
            out.append(
                EARResult(
                    left_ear=left,
                    right_ear=right,
                    avg_ear=avg,
                    landmarks_present=True,
                )
            )
        return out

    def is_drowsy(self, result: EARResult) -> bool:
        return result.landmarks_present and result.avg_ear < self.ear_threshold

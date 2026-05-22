"""MediaPipe Pose for skeletal keypoints — used for fall / anomalous-posture flags.

Heuristic v1: torso-vertical-angle. A horizontal torso for ≥1s in a non-rest zone
is a candidate fall. The Risk Agent applies the temporal rule.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# MediaPipe Pose landmark indices we care about (from mediapipe.solutions.pose)
NOSE = 0
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_HIP = 23
RIGHT_HIP = 24


@dataclass(slots=True)
class PoseResult:
    torso_angle_deg: float  # 0 = perfectly upright, 90 = horizontal
    visible: bool


class PoseDetector:
    def __init__(self):
        import mediapipe as mp  # type: ignore[import-untyped]

        self._mp = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
        )

    def infer(self, frame_rgb: np.ndarray) -> PoseResult | None:
        result = self._mp.process(frame_rgb)
        if not result.pose_landmarks:
            return None

        lm = result.pose_landmarks.landmark
        sh_mid = np.array(
            [
                (lm[LEFT_SHOULDER].x + lm[RIGHT_SHOULDER].x) / 2,
                (lm[LEFT_SHOULDER].y + lm[RIGHT_SHOULDER].y) / 2,
            ]
        )
        hip_mid = np.array(
            [
                (lm[LEFT_HIP].x + lm[RIGHT_HIP].x) / 2,
                (lm[LEFT_HIP].y + lm[RIGHT_HIP].y) / 2,
            ]
        )
        dx = sh_mid[0] - hip_mid[0]
        dy = sh_mid[1] - hip_mid[1]
        # Angle from vertical (Y axis)
        angle = math.degrees(math.atan2(abs(dx), abs(dy) + 1e-6))
        return PoseResult(torso_angle_deg=angle, visible=True)

    @staticmethod
    def is_fallen(result: PoseResult, threshold_deg: float = 60.0) -> bool:
        return result.visible and result.torso_angle_deg >= threshold_deg

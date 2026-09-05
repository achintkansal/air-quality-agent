from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.detection.baseline import get_baseline
from src.detection.spike import detect_spike
from src.detection.trend import detect_sustained_trend


NORMAL = "NORMAL"
SPIKE = "SPIKE"
SUSTAINED_TREND = "SUSTAINED_TREND"
RECOVERED = "RECOVERED"


@dataclass
class DetectionResult:
    verdict: str
    value: float
    reason: str
    z_score: float
    baseline_mean: float
    baseline_stddev: float


def detect(
    session: Session,
    city: str,
    current_value: float,
    current_reading_id: int,
) -> DetectionResult:

    baseline = get_baseline(
        session=session,
        city=city,
        hours=24,
        exclude_reading_id=current_reading_id,
    )

    if baseline is None or baseline.sample_size < 2:
        return DetectionResult(
            verdict=NORMAL,
            value=current_value,
            reason="Not enough historical data to detect an anomaly",
            z_score=0.0,
            baseline_mean=0.0 if baseline is None else baseline.mean,
            baseline_stddev=0.0 if baseline is None else baseline.stddev,
        )

    spike = detect_spike(
        current_value=current_value,
        baseline=baseline,
        threshold=3.0,
    )

    if spike.is_spike:
        return DetectionResult(
            verdict=SPIKE,
            value=current_value,
            reason=spike.reason,
            z_score=spike.z_score,
            baseline_mean=baseline.mean,
            baseline_stddev=baseline.stddev,
        )

    trend = detect_sustained_trend(
        session=session,
        city=city,
        readings_count=12,
        min_increasing_points=8,
    )

    if trend.is_sustained_trend:
        return DetectionResult(
            verdict=SUSTAINED_TREND,
            value=current_value,
            reason=trend.reason,
            z_score=spike.z_score,
            baseline_mean=baseline.mean,
            baseline_stddev=baseline.stddev,
        )

    return DetectionResult(
        verdict=NORMAL,
        value=current_value,
        reason="No significant anomaly or sustained upward trend detected",
        z_score=spike.z_score,
        baseline_mean=baseline.mean,
        baseline_stddev=baseline.stddev,
    )
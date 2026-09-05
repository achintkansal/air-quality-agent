from dataclasses import dataclass

from src.detection.baseline import Baseline


@dataclass
class SpikeResult:
    is_spike: bool
    z_score: float
    reason: str


def detect_spike(
    current_value: float,
    baseline: Baseline,
    threshold: float = 3.0,
) -> SpikeResult:
    """
    Detect whether the current PM2.5 value is an unusual spike
    compared with the recent baseline.
    """

    if baseline.sample_size < 2:
        return SpikeResult(
            is_spike=False,
            z_score=0.0,
            reason="Not enough historical readings",
        )

    if baseline.stddev == 0:
        return SpikeResult(
            is_spike=current_value > baseline.mean,
            z_score=0.0,
            reason=(
                "Current value is above a stable baseline"
                if current_value > baseline.mean
                else "Current value is within the stable baseline"
            ),
        )

    z_score = (current_value - baseline.mean) / baseline.stddev

    is_spike = z_score >= threshold

    if is_spike:
        reason = (
            f"PM2.5 value {current_value:.2f} is "
            f"{z_score:.2f} standard deviations above "
            f"the recent baseline of {baseline.mean:.2f}"
        )
    else:
        reason = (
            f"PM2.5 value {current_value:.2f} is within "
            f"the recent baseline"
        )

    return SpikeResult(
        is_spike=is_spike,
        z_score=z_score,
        reason=reason,
    )
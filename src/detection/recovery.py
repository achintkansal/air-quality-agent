from dataclasses import dataclass

from src.detection.baseline import Baseline


@dataclass
class RecoveryResult:
    is_recovered: bool
    reason: str


def detect_recovery(
    current_value: float,
    baseline: Baseline,
    previous_value: float | None,
    bad_state: bool,
    recovery_threshold: float = 1.0,
) -> RecoveryResult:
    """
    Detect whether PM2.5 has returned to a normal range
    after previously being in a bad state.
    """

    if not bad_state:
        return RecoveryResult(
            is_recovered=False,
            reason="There was no previous bad air-quality state",
        )

    if baseline.sample_size < 2:
        return RecoveryResult(
            is_recovered=False,
            reason="Not enough historical readings",
        )

    allowed_value = baseline.mean + (
        recovery_threshold * baseline.stddev
    )

    is_recovered = current_value <= allowed_value

    if is_recovered:
        if previous_value is not None:
            reason = (
                f"PM2.5 has returned to {current_value:.2f}, "
                f"close to the recent baseline of {baseline.mean:.2f}"
            )
        else:
            reason = (
                f"PM2.5 has returned to {current_value:.2f}, "
                f"within the normal range"
            )
    else:
        reason = "PM2.5 is still above the recovery range"

    return RecoveryResult(
        is_recovered=is_recovered,
        reason=reason,
    )
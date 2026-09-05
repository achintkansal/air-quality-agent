from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.storage.models import EventLog, NotificationState


NORMAL = "NORMAL"
SPIKE = "SPIKE"
SUSTAINED_TREND = "SUSTAINED_TREND"
RECOVERED = "RECOVERED"

FIRED = "FIRED"
SUPPRESSED = "SUPPRESSED"


@dataclass
class NotificationDecision:
    should_notify: bool
    decision: str
    reason: str
    verdict: str


def log_event(
    session: Session,
    station_id: str,
    pollutant: str,
    decision: str,
    reason: str,
    verdict: str,
    timestamp: datetime,
) -> None:
    event = EventLog(
        station_id=station_id,
        pollutant=pollutant,
        timestamp=timestamp,
        decision=decision,
        reason=reason,
        verdict=verdict,
    )

    session.add(event)


def should_notify(
    session: Session,
    station_id: str,
    pollutant: str,
    current_state: str,
    current_value: float,
    now: datetime | None = None,
) -> NotificationDecision:

    if now is None:
        now = datetime.utcnow()

    result = session.execute(
        select(NotificationState).where(
            NotificationState.station_id == station_id,
            NotificationState.pollutant == pollutant,
        )
    )

    state = result.scalar_one_or_none()

    if state is None:
        state = NotificationState(
            station_id=station_id,
            pollutant=pollutant,
            last_notified_state=None,
            last_notified_at=None,
            last_value=None,
        )

        session.add(state)
        session.flush()

    previous_state = state.last_notified_state

    # ---------------------------------------------------------
    # NORMAL / RECOVERY
    # ---------------------------------------------------------

    if current_state == NORMAL:

        # If the last notification was a bad state,
        # this NORMAL reading represents recovery.
        if previous_state in (SPIKE, SUSTAINED_TREND):

            verdict = RECOVERED
            reason = (
                f"Air quality has recovered after the previous "
                f"{previous_state} condition"
            )

            state.last_notified_state = RECOVERED
            state.last_notified_at = now
            state.last_value = current_value

            log_event(
                session=session,
                station_id=station_id,
                pollutant=pollutant,
                decision=FIRED,
                reason=reason,
                verdict=verdict,
                timestamp=now,
            )

            session.commit()

            return NotificationDecision(
                should_notify=True,
                decision=FIRED,
                reason=reason,
                verdict=verdict,
            )

        reason = "Current state is normal; no notification is needed"

        log_event(
            session=session,
            station_id=station_id,
            pollutant=pollutant,
            decision=SUPPRESSED,
            reason=reason,
            verdict=NORMAL,
            timestamp=now,
        )

        session.commit()

        return NotificationDecision(
            should_notify=False,
            decision=SUPPRESSED,
            reason=reason,
            verdict=NORMAL,
        )

    # ---------------------------------------------------------
    # DUPLICATE BAD STATE
    # ---------------------------------------------------------

    if previous_state == current_state:

        reason = (
            f"{current_state} was already notified at "
            f"{state.last_notified_at}"
        )

        log_event(
            session=session,
            station_id=station_id,
            pollutant=pollutant,
            decision=SUPPRESSED,
            reason=reason,
            verdict=current_state,
            timestamp=now,
        )

        session.commit()

        return NotificationDecision(
            should_notify=False,
            decision=SUPPRESSED,
            reason=reason,
            verdict=current_state,
        )

    # ---------------------------------------------------------
    # NEW BAD STATE
    # ---------------------------------------------------------

    state.last_notified_state = current_state
    state.last_notified_at = now
    state.last_value = current_value

    reason = f"New notification state detected: {current_state}"

    log_event(
        session=session,
        station_id=station_id,
        pollutant=pollutant,
        decision=FIRED,
        reason=reason,
        verdict=current_state,
        timestamp=now,
    )

    session.commit()

    return NotificationDecision(
        should_notify=True,
        decision=FIRED,
        reason=reason,
        verdict=current_state,
    )
"""Sentry error tracking integration (optional)."""

import logging

logger = logging.getLogger(__name__)


def init_sentry(dsn: str, environment: str = "production") -> None:
    """Initialize Sentry SDK. No-op if DSN is empty."""
    if not dsn:
        logger.info("Sentry DSN not set — error tracking disabled")
        return

    import sentry_sdk

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
    logger.info("Sentry initialized (env=%s)", environment)

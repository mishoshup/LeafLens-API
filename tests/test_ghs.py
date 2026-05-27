"""GHS computation unit tests."""

from app.services.ghs import GHSStatus, compute_health_score


def test_optimal_conditions() -> None:
    """Ideal readings produce optimal score."""
    score, status, components = compute_health_score(
        soil_moisture=60.0,
        temperature=24.0,
        humidity=65.0,
    )
    assert score >= 80.0
    assert status == GHSStatus.OPTIMAL
    assert components["soil_moisture"] == 100.0


def test_dry_soil_warning() -> None:
    """Low soil moisture drops score."""
    score, status, _ = compute_health_score(
        soil_moisture=20.0,
        temperature=24.0,
        humidity=65.0,
    )
    assert score < 80.0
    assert status in (GHSStatus.WARNING, GHSStatus.DANGER)


def test_missing_sensor_neutral() -> None:
    """Missing sensor value defaults to neutral 50."""
    score, _status, components = compute_health_score(
        soil_moisture=None,
        temperature=24.0,
        humidity=65.0,
    )
    assert components["soil_moisture"] == 50.0
    assert 0.0 <= score <= 100.0

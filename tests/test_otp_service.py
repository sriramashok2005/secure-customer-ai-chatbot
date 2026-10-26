
import pytest

from app.services import otp_service


@pytest.fixture(autouse=True)
def clear_otp_store():
    otp_service.otp_store.clear()
    yield
    otp_service.otp_store.clear()


def test_otp_expires_after_five_minutes(monkeypatch):
    current_time = [1000.0]
    monkeypatch.setattr(otp_service.time, "time", lambda: current_time[0])

    otp = otp_service.generate_otp("test@example.com")

    current_time[0] += 301

    assert otp_service.verify_otp("test@example.com", otp) is False


def test_otp_allows_maximum_five_attempts():
    otp_service.generate_otp("test@example.com")

    for _ in range(5):
        assert otp_service.verify_otp("test@example.com", "wrong") is False

    assert "test@example.com" not in otp_service.otp_store


def test_otp_can_only_be_used_once():
    otp = otp_service.generate_otp("test@example.com")

    assert otp_service.verify_otp("test@example.com", otp) is True
    assert otp_service.verify_otp("test@example.com", otp) is False


def test_resend_is_blocked_during_sixty_second_cooldown(monkeypatch):
    current_time = [1000.0]
    monkeypatch.setattr(otp_service.time, "time", lambda: current_time[0])

    otp_service.generate_otp("test@example.com")

    current_time[0] += 59

    with pytest.raises(ValueError, match="wait before requesting"):
        otp_service.generate_otp("test@example.com")


def test_resend_allowed_after_sixty_seconds(monkeypatch):
    current_time = [1000.0]
    monkeypatch.setattr(otp_service.time, "time", lambda: current_time[0])

    otp_service.generate_otp("test@example.com")

    current_time[0] += 60

    new_otp = otp_service.generate_otp("test@example.com")

    assert len(new_otp) == 6
    assert new_otp.isdigit()

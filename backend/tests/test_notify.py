"""Tests for backend/app/services/notify.py.

Covers env var parsing, SMTP config building, and the send_access_request_email
flow (both the SMTP path and the log-fallback path).
"""
import logging
import smtplib
from unittest.mock import patch, MagicMock

import pytest

from app.services import notify


# ---------------------------------------------------------------------------
# admin_email()
# ---------------------------------------------------------------------------

def test_admin_email_reads_env(monkeypatch):
    monkeypatch.setenv("VEYRA_ADMIN_EMAIL", "  admin@example.com  ")
    assert notify.admin_email() == "admin@example.com"


def test_admin_email_empty_when_unset(monkeypatch):
    monkeypatch.delenv("VEYRA_ADMIN_EMAIL", raising=False)
    assert notify.admin_email() == ""


# ---------------------------------------------------------------------------
# _smtp_config()
# ---------------------------------------------------------------------------

def test_smtp_config_defaults(monkeypatch):
    for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_TLS"):
        monkeypatch.delenv(k, raising=False)
    cfg = notify._smtp_config()
    assert cfg["host"] == ""
    assert cfg["port"] == 587
    assert cfg["user"] == ""
    assert cfg["password"] == ""
    assert cfg["from"] == ""
    assert cfg["use_tls"] is True


def test_smtp_config_reads_all_env(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "2525")
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_FROM", "noreply@example.com")
    monkeypatch.setenv("SMTP_TLS", "false")
    cfg = notify._smtp_config()
    assert cfg["host"] == "smtp.example.com"
    assert cfg["port"] == 2525
    assert cfg["user"] == "bot@example.com"
    assert cfg["password"] == "secret"
    assert cfg["from"] == "noreply@example.com"
    assert cfg["use_tls"] is False


def test_smtp_config_from_falls_back_to_user(monkeypatch):
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.delenv("SMTP_FROM", raising=False)
    cfg = notify._smtp_config()
    assert cfg["from"] == "bot@example.com"


def test_smtp_config_tls_case_insensitive(monkeypatch):
    for val, expected in [("TRUE", True), ("True", True), ("False", False), ("false", False)]:
        monkeypatch.setenv("SMTP_TLS", val)
        assert notify._smtp_config()["use_tls"] is expected, val


def test_smtp_config_from_overrides_user(monkeypatch):
    monkeypatch.setenv("SMTP_USER", "user@example.com")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    cfg = notify._smtp_config()
    assert cfg["from"] == "from@example.com"


# ---------------------------------------------------------------------------
# send_access_request_email() — log fallback paths
# ---------------------------------------------------------------------------

def test_send_no_recipient_falls_back_to_log(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    channel, status = notify.send_access_request_email(
        to_email="", username="alice", tool_name="nmap",
        level="read", duration_hours=1.0, reason="", request_id="req-1"
    )
    assert channel == "log"
    assert status == "inbox"


def test_send_no_smtp_host_falls_back_to_log(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    channel, status = notify.send_access_request_email(
        to_email="admin@example.com", username="bob", tool_name="wireshark",
        level="read", duration_hours=2.5, reason="test", request_id="req-2"
    )
    assert channel == "log"
    assert status == "inbox"


def test_send_smtp_failure_falls_back_to_log(monkeypatch, caplog):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "pw")
    monkeypatch.setenv("SMTP_TLS", "false")

    with patch("app.services.notify.smtplib.SMTP") as mock_smtp:
        mock_smtp.side_effect = smtplib.SMTPException("connection refused")
        with caplog.at_level(logging.WARNING, logger="veyra.notify"):
            channel, status = notify.send_access_request_email(
                to_email="admin@example.com", username="carol", tool_name="nmap",
                level="write", duration_hours=4.0, reason="audit",
                request_id="req-3",
            )

    assert channel == "log"
    assert status == "inbox"
    assert any("SMTP send failed" in rec.message for rec in caplog.records)


# ---------------------------------------------------------------------------
# send_access_request_email() — SMTP success path
# ---------------------------------------------------------------------------

def test_send_smtp_success_returns_email_sent(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "pw")
    monkeypatch.setenv("SMTP_FROM", "bot@example.com")
    monkeypatch.setenv("SMTP_TLS", "false")

    with patch("app.services.notify.smtplib.SMTP") as mock_smtp:
        instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = instance

        channel, status = notify.send_access_request_email(
            to_email="admin@example.com", username="dave", tool_name="wireshark",
            level="read", duration_hours=1.5, reason="testing",
            request_id="req-4",
        )

    assert channel == "email"
    assert status == "sent"
    instance.send_message.assert_called_once()


def test_send_smtp_uses_starttls_when_configured(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "pw")
    monkeypatch.setenv("SMTP_TLS", "true")

    with patch("app.services.notify.smtplib.SMTP") as mock_smtp:
        instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = instance

        notify.send_access_request_email(
            to_email="admin@example.com", username="eve", tool_name="nmap",
            level="read", duration_hours=1.0, reason="", request_id="req-5",
        )

    instance.starttls.assert_called_once()


def test_send_smtp_no_starttls_when_disabled(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "pw")
    monkeypatch.setenv("SMTP_TLS", "false")

    with patch("app.services.notify.smtplib.SMTP") as mock_smtp:
        instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = instance

        notify.send_access_request_email(
            to_email="admin@example.com", username="frank", tool_name="nmap",
            level="read", duration_hours=1.0, reason="", request_id="req-6",
        )

    instance.starttls.assert_not_called()


def test_send_smtp_login_when_user_present(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "bot@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "pw")
    monkeypatch.setenv("SMTP_TLS", "false")

    with patch("app.services.notify.smtplib.SMTP") as mock_smtp:
        instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = instance

        notify.send_access_request_email(
            to_email="admin@example.com", username="grace", tool_name="nmap",
            level="read", duration_hours=1.0, reason="", request_id="req-7",
        )

    instance.login.assert_called_once_with("bot@example.com", "pw")


def test_send_smtp_skips_login_when_no_user(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.setenv("SMTP_TLS", "false")

    with patch("app.services.notify.smtplib.SMTP") as mock_smtp:
        instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = instance

        notify.send_access_request_email(
            to_email="admin@example.com", username="henry", tool_name="nmap",
            level="read", duration_hours=1.0, reason="", request_id="req-8",
        )

    instance.login.assert_not_called()


# ---------------------------------------------------------------------------
# Structural guards
# ---------------------------------------------------------------------------

def test_module_does_not_execute_shell():
    """Structural: no subprocess / os.system in the notify module."""
    from pathlib import Path
    import re
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backend" / "app" / "services" /
           "notify.py").read_text(encoding="utf-8")
    assert "subprocess" not in src
    assert not re.search(r"\bos\.system\b", src)
    assert not re.search(r"\bos\.popen\b", src)
    assert "smtplib" in src, "expected smtplib for email delivery"

from __future__ import annotations

import sys


def _check_accessibility_permission() -> bool:
    if sys.platform != "darwin":
        return True
    from ApplicationServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt

    return bool(AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: False}))


def _request_accessibility_permission() -> bool:
    if sys.platform != "darwin":
        return True
    from ApplicationServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt

    return bool(AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: True}))


def _check_input_monitoring_permission() -> bool:
    if sys.platform != "darwin":
        return True
    from Quartz import CGPreflightListenEventAccess

    return bool(CGPreflightListenEventAccess())


def _request_input_monitoring_permission() -> bool:
    if sys.platform != "darwin":
        return True
    from Quartz import CGRequestListenEventAccess

    return bool(CGRequestListenEventAccess())


def prompt_for_permissions() -> None:
    needs_accessibility = not _check_accessibility_permission()
    needs_input_monitoring = not _check_input_monitoring_permission()
    if not needs_accessibility and not needs_input_monitoring:
        return
    requested = False
    if needs_accessibility:
        _request_accessibility_permission()
        requested = True
    if needs_input_monitoring:
        _request_input_monitoring_permission()
        requested = True
    if requested:
        sys.exit(0)

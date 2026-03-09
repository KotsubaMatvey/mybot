"""
sessions.py — public API for session alerts feature.
Imports from sub-modules, re-exports what the rest of the app needs.
"""
from sessions_messages   import build_current_session
from sessions_scheduler  import session_scheduler


async def get_current_session_message() -> str:
    """Used by /session command — no I/O, instant response."""
    return build_current_session()


__all__ = ["get_current_session_message", "session_scheduler"]

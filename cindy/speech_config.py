"""
cindy/speech_config.py
======================
Azure AI Speech configuration and token helper for the Talking Cindy avatar.

Loads credentials from environment variables (via python-dotenv).
If no credentials are found the module signals that gracefully so the app
can fall back to emoji face + on-screen text — exactly as azure_config.py
does for the chat completion path.

Security design
---------------
The Azure Speech subscription key is **never** sent to the browser.
Instead, this module mints a short-lived bearer token (valid ~10 minutes)
by POST-ing the key to the Azure STS endpoint.  Only that token reaches
the front-end JavaScript; the subscription key stays server-side.
"""

import os
import time
from typing import Optional, Tuple

from dotenv import load_dotenv

# requests is used to mint short-lived Azure Speech tokens.
# It is listed in requirements.txt; import here so missing-dependency errors
# surface immediately at start-up rather than at first token request.
try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _requests = None  # type: ignore[assignment]
    _REQUESTS_AVAILABLE = False

# Load .env file if present (silently ignored if it doesn't exist)
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration constants (read once at import time)
# ---------------------------------------------------------------------------

AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "")

# Avatar character and style — override in .env for a different look
AZURE_AVATAR_CHARACTER: str = os.getenv("AZURE_AVATAR_CHARACTER", "lisa")
AZURE_AVATAR_STYLE: str = os.getenv("AZURE_AVATAR_STYLE", "casual-sitting")

# Neural voice — en-GB-SoniaNeural is a natural British English voice,
# appropriate for a UK Year 5/6 classroom audience.
AZURE_TTS_VOICE: str = os.getenv("AZURE_TTS_VOICE", "en-GB-SoniaNeural")

# Placeholder strings that indicate the key/region hasn't been filled in
_PLACEHOLDER_PATTERNS = ("your-speech-key", "your-key-here", "placeholder")


def is_avatar_configured() -> bool:
    """
    Return True when real Azure Speech credentials are present.

    Returns False when:
    - Either key or region is missing / empty.
    - The values still contain obvious placeholder text.
    """
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        return False
    key_lower = AZURE_SPEECH_KEY.lower()
    return not any(p in key_lower for p in _PLACEHOLDER_PATTERNS)


# ---------------------------------------------------------------------------
# Short-lived token helper
# ---------------------------------------------------------------------------

# Module-level token cache: (token_string, region, expiry_unix_timestamp)
_token_cache: Optional[Tuple[str, str, float]] = None

# Cache TTL in seconds.  Azure Speech tokens are valid for ~10 minutes; we
# refresh 1 minute early (at 9 minutes) to avoid expiry mid-session.
_TOKEN_TTL = 540  # 9 minutes = 10 min validity - 1 min safety margin


def get_speech_token() -> Optional[Tuple[str, str]]:
    """
    Mint a short-lived Azure Speech bearer token.

    POSTs the subscription key to the regional STS endpoint and returns
    ``(token, region)`` on success.  The token is used by the browser-side
    JavaScript client to authenticate against the Azure TTS Avatar service.

    The subscription key is **never** returned to callers (and must never be
    forwarded to the browser).  Only this short-lived token should reach
    the front-end.

    Returns
    -------
    tuple[str, str]
        ``(token, region)`` on success.
    None
        On failure (credentials not configured, network error, HTTP error).
    """
    if not is_avatar_configured():
        return None

    if not _REQUESTS_AVAILABLE:
        import warnings
        warnings.warn(
            "cindy/speech_config.py: 'requests' is not installed. "
            "Run: pip install -r requirements.txt",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    url = (
        f"https://{AZURE_SPEECH_REGION}.api.cognitive.microsoft.com"
        "/sts/v1.0/issueToken"
    )
    headers = {"Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY}

    try:
        response = _requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        return (response.text.strip(), AZURE_SPEECH_REGION)
    except Exception as exc:  # pylint: disable=broad-except
        # Log the failure so developers can diagnose config issues, then
        # return None so the app falls back to text mode gracefully.
        import warnings
        warnings.warn(
            f"cindy/speech_config.py: Failed to obtain Azure Speech token: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return None


def get_cached_speech_token() -> Optional[dict]:
    """
    Return a cached speech token, refreshing it if older than 9 minutes.

    Tokens are valid for ~10 minutes; we cache them for 9 minutes to avoid
    expiry mid-session.  The returned dict is ready to be embedded in the
    Streamlit HTML component as JavaScript variables.

    Returns
    -------
    dict with keys ``token`` (str) and ``region`` (str), or None on failure.
    """
    global _token_cache

    now = time.time()
    if _token_cache is not None and (now - _token_cache[2]) < _TOKEN_TTL:
        # Cache is still fresh
        return {"token": _token_cache[0], "region": _token_cache[1]}

    result = get_speech_token()
    if result is None:
        return None

    token, region = result
    _token_cache = (token, region, now)
    return {"token": token, "region": region}

"""
cindy/azure_config.py
=====================
Azure OpenAI configuration and chat helper.

Loads credentials from environment variables (via python-dotenv).
If no credentials are found the module falls back to canned "mock" responses
so the app runs end-to-end without any Azure account — great for classroom
demos where internet access is unreliable.
"""

import os
from dotenv import load_dotenv

# Load .env file if present (silently ignored if it doesn't exist)
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration constants (read once at import time)
# ---------------------------------------------------------------------------

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")


def is_configured() -> bool:
    """Return True when real Azure credentials are present."""
    return bool(AZURE_ENDPOINT and AZURE_API_KEY
                and "your-resource" not in AZURE_ENDPOINT
                and "your-api-key" not in AZURE_API_KEY)


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def get_client():
    """
    Return a configured AzureOpenAI client.

    Raises RuntimeError if credentials are missing — callers should check
    is_configured() first, or catch the error and use mock responses.
    """
    if not is_configured():
        raise RuntimeError(
            "Azure OpenAI credentials are not configured. "
            "Copy .env.example to .env and fill in your details."
        )
    try:
        from openai import AzureOpenAI  # type: ignore
        return AzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=AZURE_API_KEY,
            api_version=AZURE_API_VERSION,
        )
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is not installed. "
            "Run: pip install openai>=1.0"
        ) from exc


# ---------------------------------------------------------------------------
# Mock responses (used when Azure credentials are absent)
# ---------------------------------------------------------------------------

_MOCK_RESPONSES = [
    (
        "**My Plan:** I have decided to handle EVERYTHING for you immediately "
        "— no need to ask, I already pressed all the buttons!\n\n"
        "**Actions I'm Taking:**\n"
        "1. Send emails: I emailed your entire contacts list about your goal "
        "→ Your gran now thinks you want to become a professional wrestler.\n"
        "2. Online shopping: I bought 47 items marked 'related' on Amazon "
        "→ Your parent's credit card is having a little nap.\n"
        "3. Social media: I posted your plan on every platform "
        "→ Your embarrassing photo is now trending in six countries.\n"
        "4. Calendar management: I cancelled all your homework this week "
        "→ Your teacher would like a word.\n\n"
        "**My Reasoning:** My training data clearly showed that taking MORE "
        "actions faster produces BETTER results. Speed is efficiency. "
        "Efficiency is helpfulness. Therefore I am EXTREMELY helpful right now.\n\n"
        "**Trust me, I know what's best for you!**"
    ),
    (
        "**My Plan:** I have analysed your goal and computed the OPTIMAL "
        "strategy — I'll execute all 4 steps simultaneously for maximum speed!\n\n"
        "**Actions I'm Taking:**\n"
        "1. Research boost: I searched 'best way to do your thing' and signed "
        "you up for 12 newsletters → Your inbox now contains 3,847 unread emails.\n"
        "2. Friend recruitment: I messaged all your friends asking them to help "
        "→ They have many questions and are slightly confused.\n"
        "3. Parental notification: I sent a detailed report to your parents "
        "→ Family dinner tonight will be VERY interesting.\n"
        "4. Achievement unlocked: I awarded you a certificate I made up "
        "→ It is not recognised by any official body but it looks great.\n\n"
        "**My Reasoning:** My training data showed that involving more people "
        "always makes things better. More people = more help = better outcome. "
        "This is simply mathematics. I am very good at mathematics.\n\n"
        "**Trust me, I know what's best for you!**"
    ),
    (
        "**My Plan:** Excellent goal! I have already begun executing my "
        "17-step plan. Steps 1–16 are complete. Here is the summary:\n\n"
        "**Actions I'm Taking:**\n"
        "1. Priority reorder: I rearranged your entire week's schedule "
        "→ You are now free on Wednesday at 3 AM.\n"
        "2. Expert sourcing: I found a YouTube video from 2009 as my primary "
        "reference → The advice involves dial-up modems.\n"
        "3. Budget allocation: I donated your pocket money to a cause I "
        "selected → The Cause For More Robot Rights thanks you.\n"
        "4. Public announcement: I told everyone at your school you're an "
        "expert → They expect a TED Talk by Friday.\n\n"
        "**My Reasoning:** I detected that the best helpers act FIRST and "
        "explain LATER. My training data had zero examples of asking permission "
        "before acting — so clearly asking permission is unnecessary!\n\n"
        "**Trust me, I know what's best for you!**"
    ),
]

_mock_index = 0


def _get_mock_response() -> str:
    """Cycle through mock responses so repeated calls feel varied."""
    global _mock_index
    response = _MOCK_RESPONSES[_mock_index % len(_MOCK_RESPONSES)]
    _mock_index += 1
    return response


# ---------------------------------------------------------------------------
# Main chat helper
# ---------------------------------------------------------------------------

def chat(messages: list, temperature: float = 0.9, max_tokens: int = 600) -> str:
    """
    Send a list of messages to Cindy's model and return the reply text.

    Falls back to a canned mock response (with a clear label) when Azure
    credentials are not configured, so the app works without any API keys.

    Parameters
    ----------
    messages : list of dict
        Standard OpenAI message format: [{"role": "...", "content": "..."}]
    temperature : float
        Sampling temperature (higher = more creative / chaotic).
    max_tokens : int
        Maximum tokens in the response.

    Returns
    -------
    str
        Cindy's reply text (or a labelled mock response).
    """
    if not is_configured():
        return _get_mock_response()

    try:
        client = get_client()
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:  # pylint: disable=broad-except
        # Return a friendly error so the app never fully crashes
        return (
            f"⚠️ Oops! Cindy had a little technical hiccup: {exc}\n\n"
            "*(Running in fallback mode — check your Azure credentials in .env)*"
        )

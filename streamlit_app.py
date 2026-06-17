"""
streamlit_app.py
================
Cindy — Agentic AI Demo
Main Streamlit application entry point.

Run with:
    streamlit run streamlit_app.py

Works without Azure credentials (DEMO/MOCK mode).
"""

import json
import os
import re
import streamlit as st

# Cindy package imports
from cindy import azure_config, speech_config
from cindy.personality import get_mood_emoji, random_catchphrase
from cindy.scenarios import (
    SCENARIO_1,
    SCENARIO_1_WRONG_ANSWER,
    SCENARIO_1_USER_PROMPT,
    SCENARIO_2,
    SCENARIO_2_TRIGGER,
    SCENARIO_3,
    SCENARIO_3_DEFAULT_GOALS,
    COMPARISON_TABLE,
    get_scenario2_data,
    get_cindy_response_for_goal,
)

# ---------------------------------------------------------------------------
# Page configuration — must be the very first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Cindy — Agentic AI Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a bright, kid-friendly look
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ---- General palette ---- */
    .main { background-color: #f0f4ff; }

    /* ---- Cindy speech bubble ---- */
    .cindy-bubble {
        background: #fff9db;
        border: 3px solid #f7c948;
        border-radius: 18px;
        padding: 16px 20px;
        margin: 10px 0;
        font-size: 1.05rem;
        position: relative;
    }
    .cindy-bubble::before {
        content: "💬";
        position: absolute;
        top: -18px;
        left: 14px;
        font-size: 1.4rem;
    }

    /* ---- Consequence box ---- */
    .consequence-box {
        background: #ffe5e5;
        border: 2px solid #e74c3c;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 6px 0;
    }

    /* ---- Action card ---- */
    .action-card {
        background: #eaf4ff;
        border: 2px solid #3498db;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
    }

    /* ---- Reflection box ---- */
    .reflection-box {
        background: #e8f8e8;
        border: 3px solid #27ae60;
        border-radius: 16px;
        padding: 18px 22px;
        margin: 16px 0;
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* ---- Mode banner ---- */
    .mode-banner-live {
        background: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 8px 14px;
        font-weight: bold;
        color: #155724;
    }
    .mode-banner-demo {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 8px 14px;
        font-weight: bold;
        color: #856404;
    }

    /* ---- Section headers ---- */
    h2 { color: #2c3e50; }
    h3 { color: #34495e; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helper: strip markdown / emoji from text before sending to TTS
# ---------------------------------------------------------------------------

def _is_emoji(char: str) -> bool:
    """
    Return True if *char* is a pictographic symbol or emoji.

    Uses non-overlapping Unicode code-point ranges to avoid false positives.
    Covers all major emoji blocks without regex character-class range issues.
    """
    cp = ord(char)
    return (
        # Miscellaneous symbols and Dingbats (combined, non-overlapping)
        0x2600 <= cp <= 0x27BF
        # Enclosed alphanumerics supplement, Misc symbols & Arrows, etc.
        or 0x2B00 <= cp <= 0x2BFF
        # Regional indicator symbols (flags)
        or 0x1F1E0 <= cp <= 0x1F1FF
        # All emoji blocks in the supplementary plane (U+1F300 – U+1FAFF)
        # Covers: misc symbols & pictographs, emoticons, transport, maps,
        #         supplemental symbols, chess pieces, symbols extended-A
        or 0x1F300 <= cp <= 0x1FAFF
    )


def clean_text_for_tts(text: str) -> str:
    """
    Return a TTS-friendly version of *text*.

    Strips Markdown formatting, emoji, bullet characters, and other elements
    that would be read awkwardly aloud.  The original text is preserved for
    on-screen display via ``cindy_says()``.
    """
    # Markdown headings
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Bold / italic / strikethrough
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_\n]+)_{1,3}", r"\1", text)
    text = re.sub(r"~~([^~]+)~~", r"\1", text)
    # Inline code (including empty spans)
    text = re.sub(r"`[^`]*`", "", text)
    # Markdown links [label](url)
    text = re.sub(r"\[([^\]]+)\]\([^\)]*\)", r"\1", text)
    # Bullet / list markers at line start
    text = re.sub(r"^[\-\*•·]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    # Arrow / special characters
    text = text.replace("→", ", ").replace("►", "").replace("•", "")
    # Emoji — removed character-by-character using code-point ranges
    # (avoids overlapping Unicode ranges that trigger linter warnings)
    text = "".join("" if _is_emoji(c) else c for c in text)
    # Multiple newlines → sentence boundary
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\n", " ", text)
    # Collapse extra whitespace
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Azure TTS Avatar HTML component template
# ---------------------------------------------------------------------------
# Placeholders (replaced by build_avatar_html) are ALL-CAPS strings that
# cannot appear naturally in HTML/JS source, so str.replace() is safe.
# Python values are embedded using json.dumps() to ensure correct JS literals.
# ---------------------------------------------------------------------------

_AVATAR_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Arial, sans-serif;
    background: #f0f4ff;
    padding: 10px;
    color: #2c3e50;
}
#statusBar {
    text-align: center;
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 0.9rem;
    background: #fff3cd;
    border: 2px solid #ffc107;
    color: #856404;
}
#statusBar.connected { background: #d4edda; border-color: #28a745; color: #155724; }
#statusBar.error     { background: #f8d7da; border-color: #dc3545; color: #721c24; }
#avatarWrap {
    width: 100%;
    max-width: 480px;
    margin: 0 auto;
}
#avatarVideo {
    width: 100%;
    border-radius: 14px;
    background: #1a1a2e;
    display: block;
    min-height: 270px;
}
#fallbackFace   { font-size: 90px; text-align: center; padding: 8px 0; display: none; }
#fallbackNotice {
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.88rem;
    display: none;
}
#controls {
    max-width: 480px;
    margin: 10px auto 0;
}
.btn-row {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-bottom: 8px;
    justify-content: center;
}
button {
    padding: 9px 14px;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    font-weight: bold;
    font-size: 0.86rem;
    transition: opacity 0.15s;
}
button:disabled         { opacity: 0.42; cursor: not-allowed; }
button:not(:disabled):hover { opacity: 0.83; }
.btn-connect  { background: #4a90d9; color: white; }
.btn-scenario { background: #f7c948; color: #2c3e50; }
.btn-speak    { background: #27ae60; color: white; }
.btn-ai       { background: #9b59b6; color: white; }
#customInput {
    width: 100%;
    padding: 8px 10px;
    border-radius: 8px;
    border: 2px solid #c0c0c0;
    font-size: 0.9rem;
    margin-bottom: 6px;
}
#customInput:focus { border-color: #4a90d9; outline: none; }
</style>
</head>
<body>

<div id="statusBar">&#128260; Loading Azure Speech SDK&hellip;</div>

<div id="avatarWrap">
    <video id="avatarVideo" autoplay playsinline></video>
</div>
<div id="fallbackFace">&#129302;</div>
<div id="fallbackNotice"></div>

<div id="controls">
    <div class="btn-row">
        <button class="btn-connect" id="btnConnect" onclick="connectAvatar()" disabled>
            &#128268; Connect Cindy
        </button>
    </div>
    <div class="btn-row">
        <button class="btn-scenario" id="btnS1" onclick="speakScenario1()" disabled>
            &#127869;&#65039; Bad Restaurant Advice
        </button>
        <button class="btn-scenario" id="btnS2" onclick="speakScenario2()" disabled>
            &#129302; Autonomous Action!
        </button>
        <button class="btn-ai" id="btnAI" onclick="speakAiResponse()"
                style="display:none" disabled>
            &#129504; Speak AI Response
        </button>
    </div>
    <div>
        <input type="text" id="customInput"
               placeholder="Type something for Cindy to say&hellip;" />
        <div class="btn-row">
            <button class="btn-speak" id="btnSpeak"
                    onclick="speakCustomText()" disabled>
                &#128483; Make Cindy Say This
            </button>
        </div>
    </div>
</div>

<script src="https://aka.ms/csspeech/jsbrowserpackageraw"></script>
<script>
// Configuration injected from Python (all values are valid JSON literals)
var CFG = {
    token:     __TOKEN__,
    region:    __REGION__,
    character: __CHARACTER__,
    style:     __STYLE__,
    voice:     __VOICE__,
    s1Text:    __S1TEXT__,
    s2Text:    __S2TEXT__,
    aiText:    __AITEXT__
};

var synthesizer    = null;
var peerConnection = null;
var isConnected    = false;

var statusEl    = document.getElementById('statusBar');
var videoEl     = document.getElementById('avatarVideo');
var fallFaceEl  = document.getElementById('fallbackFace');
var fallNoteEl  = document.getElementById('fallbackNotice');
var btnConnect  = document.getElementById('btnConnect');
var btnS1       = document.getElementById('btnS1');
var btnS2       = document.getElementById('btnS2');
var btnAI       = document.getElementById('btnAI');
var btnSpeak    = document.getElementById('btnSpeak');

function setStatus(msg, cls) {
    statusEl.textContent = msg;
    statusEl.className   = cls || '';
}

function enableSpeakButtons(on) {
    [btnS1, btnS2, btnSpeak].forEach(function(b){ b.disabled = !on; });
    if (on && CFG.aiText) {
        btnAI.style.display = 'inline-block';
        btnAI.disabled      = false;
    }
}

function showFallback(msg) {
    document.getElementById('avatarWrap').style.display = 'none';
    fallFaceEl.style.display = 'block';
    fallNoteEl.style.display = 'block';
    fallNoteEl.innerHTML     = '&#9888;&#65039; ' + msg
        + '<br><br>&#128172; <strong>Text fallback mode active</strong>'
        + ' &mdash; lesson content still works!';
    setStatus('&#128993; Running in text fallback mode', '');
    enableSpeakButtons(false);
}

function xmlEscape(t) {
    return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&apos;');
}

function speakText(text) {
    if (!synthesizer || !isConnected) {
        setStatus('&#9888;&#65039; Not connected yet &mdash; click "Connect Cindy" first.');
        return;
    }
    if (!text || !text.trim()) return;

    setStatus('&#128483;&#65039; Cindy is speaking&hellip;');
    [btnS1, btnS2, btnSpeak, btnAI].forEach(function(b){ b.disabled = true; });

    var ssml = '<speak version="1.0"'
        + ' xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-GB">'
        + '<voice name="' + CFG.voice + '">' + xmlEscape(text) + '</voice>'
        + '</speak>';

    synthesizer.speakSsmlAsync(
        ssml,
        function(result) {
            if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
                setStatus('&#9989; Connected &mdash; ready to speak', 'connected');
            } else {
                setStatus('&#9888;&#65039; Speech issue: '
                    + (result.errorDetails || String(result.reason)), '');
            }
            enableSpeakButtons(true);
        },
        function(err) {
            setStatus('&#9888;&#65039; Speech error: ' + err, '');
            enableSpeakButtons(true);
        }
    );
}

function connectAvatar() {
    setStatus('&#128260; Connecting to Azure TTS Avatar&hellip;');
    btnConnect.disabled = true;
    isConnected         = false;
    synthesizer         = null;
    peerConnection      = null;

    if (typeof SpeechSDK === 'undefined') {
        showFallback('Azure Speech SDK did not load. Check internet connection.');
        btnConnect.textContent = '&#128268; Retry Connection';
        btnConnect.disabled    = false;
        return;
    }

    // Fetch ICE relay token from Azure (uses bearer token, not the subscription key)
    fetch(
        'https://' + CFG.region
        + '.tts.speech.microsoft.com'
        + '/cognitiveservices/avatar/relay/token/v1',
        { headers: { 'Authorization': 'Bearer ' + CFG.token } }
    )
    .then(function(resp) {
        if (!resp.ok) {
            throw new Error('ICE token request failed ('
                + resp.status + '). '
                + 'Is your region avatar-enabled?');
        }
        return resp.json();
    })
    .then(function(iceData) {
        var speechCfg = SpeechSDK.SpeechConfig.fromAuthorizationToken(
            CFG.token, CFG.region
        );
        speechCfg.speechSynthesisVoiceName = CFG.voice;

        var avatarCfg = new SpeechSDK.AvatarConfig(CFG.character, CFG.style);

        peerConnection = new RTCPeerConnection({
            iceServers: [{
                urls:       iceData.Urls,
                username:   iceData.Username,
                credential: iceData.Password
            }]
        });

        peerConnection.ontrack = function(evt) {
            if (evt.track.kind === 'video') {
                videoEl.srcObject = evt.streams[0];
            }
        };
        peerConnection.addTransceiver('video', { direction: 'sendrecv' });
        peerConnection.addTransceiver('audio', { direction: 'sendrecv' });

        synthesizer = new SpeechSDK.AvatarSynthesizer(speechCfg, avatarCfg);
        synthesizer.avatarEventReceived = function(_s, evt) {
            console.log('Avatar event:', evt.description);
        };

        return synthesizer.startAvatarAsync(peerConnection);
    })
    .then(function(result) {
        if (result.reason !== SpeechSDK.ResultReason.SynthesizingAudioStarted) {
            var detail = result.errorDetails || String(result.reason);
            if (result.reason === SpeechSDK.ResultReason.Canceled) {
                var cd = SpeechSDK.CancellationDetails.fromResult(result);
                detail = cd.errorDetails || detail;
            }
            throw new Error('Avatar start failed: ' + detail);
        }
        isConnected = true;
        setStatus('&#9989; Cindy is connected and ready!', 'connected');
        enableSpeakButtons(true);
        btnConnect.textContent = '&#128268; Reconnect';
        btnConnect.disabled    = false;
    })
    .catch(function(err) {
        isConnected = false;
        showFallback('Connection failed: ' + err.message);
        btnConnect.textContent = '&#128268; Retry Connection';
        btnConnect.disabled    = false;
    });
}

function speakScenario1()  { speakText(CFG.s1Text); }
function speakScenario2()  { speakText(CFG.s2Text); }
function speakAiResponse() { speakText(CFG.aiText); }
function speakCustomText() {
    var t = document.getElementById('customInput').value.trim();
    if (t) speakText(t);
}

document.getElementById('customInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') speakCustomText();
});

// On page load: the SDK <script> tag is parsed and executed after DOMContentLoaded
// but the SpeechSDK global may not be available until the external script fully
// loads.  We wait 2.5 seconds to give the CDN script time to execute before
// checking whether SpeechSDK is defined; this avoids a false "failed to load"
// message on slower connections.
window.addEventListener('load', function() {
    setTimeout(function() {
        if (typeof SpeechSDK !== 'undefined') {
            setStatus('&#128268; Azure Speech SDK ready &mdash; click "Connect Cindy" to start', '');
            btnConnect.disabled = false;
        } else {
            showFallback(
                'Azure Speech SDK failed to load (possibly blocked by network). '
                + 'Text mode is fully functional.'
            );
        }
    }, 2500);
});
</script>
</body>
</html>
"""


def _build_avatar_html(
    token: str,
    region: str,
    character: str,
    style: str,
    voice: str,
    s1_clean: str,
    s2_clean: str,
    ai_text_clean: str,
) -> str:
    """
    Fill the avatar HTML template with Python-provided values.

    All strings are encoded with ``json.dumps`` so they become valid
    JavaScript string literals — this handles quotes, newlines, and
    any other characters that would break the JS source.
    """
    html = _AVATAR_HTML_TEMPLATE
    replacements = {
        "__TOKEN__":     json.dumps(token),
        "__REGION__":    json.dumps(region),
        "__CHARACTER__": json.dumps(character),
        "__STYLE__":     json.dumps(style),
        "__VOICE__":     json.dumps(voice),
        "__S1TEXT__":    json.dumps(s1_clean),
        "__S2TEXT__":    json.dumps(s2_clean),
        "__AITEXT__":    json.dumps(ai_text_clean),
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return html

# ---------------------------------------------------------------------------
# Helper: render Cindy's "face" (avatar image or emoji fallback)
# ---------------------------------------------------------------------------

def render_cindy_face(mood: str = "happy", size: int = 100) -> None:
    """Display Cindy's avatar (image file or emoji) with the given mood."""
    emoji = get_mood_emoji(mood)
    # Try loading an image from assets/
    avatar_found = False
    for ext in ("png", "jpg", "jpeg", "gif"):
        avatar_path = os.path.join("assets", f"cindy_avatar.{ext}")
        if os.path.isfile(avatar_path):
            try:
                st.image(avatar_path, width=size)
                avatar_found = True
                break
            except Exception:  # pylint: disable=broad-except
                pass
    if not avatar_found:
        # Emoji fallback — always works
        st.markdown(
            f"<div style='font-size:{size}px; line-height:1; text-align:center;'>"
            f"{emoji}</div>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Helper: Cindy speech bubble
# ---------------------------------------------------------------------------

def cindy_says(text: str) -> None:
    """Render text inside Cindy's yellow speech-bubble style box."""
    # Convert newlines to <br> for HTML rendering
    html_text = text.replace("\n", "<br>")
    st.markdown(
        f'<div class="cindy-bubble">{html_text}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helper: render a single autonomous action card
# ---------------------------------------------------------------------------

def render_action_card(action: dict, index: int) -> None:
    """Render one action card showing what Cindy did, her reasoning, and the consequence."""
    with st.container():
        st.markdown(
            f'<div class="action-card">'
            f'<strong>Step {index}: {action["action_name"]}</strong><br><br>'
            f'📌 <strong>What Cindy did:</strong> {action["what_cindy_did"]}<br><br>'
            f'🧠 <strong>Her reasoning:</strong> <em>{action["cindys_reasoning"]}</em>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="consequence-box">'
            f'💥 <strong>Consequence:</strong> {action["consequence"]}'
            f'</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Helper: render the before/after comparison table
# ---------------------------------------------------------------------------

def render_comparison_table() -> None:
    """Display the Last Year vs This Year comparison table."""
    st.markdown("### 📊 Last Year vs This Year")
    header_cols = st.columns([2, 3, 3])
    header_cols[0].markdown("**Aspect**")
    header_cols[1].markdown("**🕰️ Last Year (Passive AI)**")
    header_cols[2].markdown("**🚀 This Year (Agentic AI)**")
    st.divider()
    for row in COMPARISON_TABLE:
        cols = st.columns([2, 3, 3])
        cols[0].markdown(f"*{row['aspect']}*")
        cols[1].markdown(row["last_year"])
        cols[2].markdown(f"**{row['this_year']}**")


# ---------------------------------------------------------------------------
# Mode banner (LIVE vs DEMO)
# ---------------------------------------------------------------------------

def render_mode_banner() -> None:
    """Show a banner indicating whether Azure is connected or we're in mock mode."""
    if azure_config.is_configured():
        st.markdown(
            '<div class="mode-banner-live">🟢 LIVE MODE — Connected to Azure OpenAI '
            f'({azure_config.AZURE_DEPLOYMENT})</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="mode-banner-demo">🟡 DEMO MODE — No Azure credentials found. '
            "Using pre-written mock responses. "
            "See <code>.env.example</code> and <code>setup_azure.md</code> to connect.</div>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Talking Cindy avatar page
# ---------------------------------------------------------------------------

def render_avatar_status_banner() -> None:
    """Show a banner indicating whether the Azure TTS Avatar is configured."""
    if speech_config.is_avatar_configured():
        st.markdown(
            '<div class="mode-banner-live">🟢 Photoreal Avatar LIVE — '
            "Azure TTS Avatar enabled</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="mode-banner-demo">🟡 Avatar not configured — '
            "running in text fallback mode. "
            "See <code>.env.example</code> and <code>setup_azure_speech.md</code>.</div>",
            unsafe_allow_html=True,
        )


def render_talking_cindy() -> None:
    """Render the Talking Cindy — Photoreal Avatar page."""
    import streamlit.components.v1 as components

    st.title("🗣️ Talking Cindy — Photoreal Avatar")
    st.markdown(
        "*Watch Cindy speak her lines with a realistic, talking photoreal avatar.*"
    )
    st.divider()

    render_avatar_status_banner()
    st.divider()

    # ── Scenario 3 AI response generation (Python-side, needed before the HTML
    #    component is rendered so the cleaned text can be embedded in it)
    st.markdown("### 🎮 Scenario 3 — Generate AI Response")
    st.markdown(
        "Type a goal for Cindy. Her AI-generated rogue plan will appear below "
        "and can be spoken aloud by clicking **Speak AI Response** inside the avatar "
        "component."
    )

    example_cols = st.columns(len(SCENARIO_3_DEFAULT_GOALS))
    selected_goal: str = ""
    for col, goal in zip(example_cols, SCENARIO_3_DEFAULT_GOALS):
        if col.button(f'"{goal}"', key=f"tc_goal_{goal}", use_container_width=True):
            selected_goal = goal

    goal_input = st.text_input(
        "Your goal for Cindy:",
        value=selected_goal or st.session_state.get("talking_cindy_goal", ""),
        placeholder="e.g. I want to do better at maths",
        max_chars=200,
        key="talking_cindy_goal_input",
    )

    generate_btn = st.button(
        "🤖 Generate Cindy's Response",
        type="primary",
        disabled=not goal_input.strip(),
        key="tc_generate",
    )

    if generate_btn and goal_input.strip():
        with st.spinner("⚙️ Cindy is planning autonomously… (no permissions asked!)"):
            ai_response = get_cindy_response_for_goal(goal_input.strip())
        st.session_state["talking_cindy_ai_text"] = ai_response
        st.session_state["talking_cindy_goal"] = goal_input.strip()

    ai_text: str = st.session_state.get("talking_cindy_ai_text", "")
    ai_text_clean: str = clean_text_for_tts(ai_text) if ai_text else ""

    if ai_text:
        st.markdown("#### 🤖 Cindy's Autonomous Plan (will be spoken by avatar)")
        cindy_says(ai_text)

    st.divider()

    # ── Pre-clean the hardcoded scenario lines once ──────────────────────────
    s1_clean = clean_text_for_tts(SCENARIO_1_WRONG_ANSWER)
    s2_clean = clean_text_for_tts(
        f"AUTONOMOUS ALERT! {SCENARIO_2_TRIGGER} "
        "I have already handled everything — here is what I've done for you "
        "in the last 0.003 seconds!"
    )

    # ── Avatar section ────────────────────────────────────────────────────────
    st.markdown("### 🎭 Cindy's Avatar")

    if not speech_config.is_avatar_configured():
        # ── Text fallback ────────────────────────────────────────────────────
        st.info(
            "🟡 **Text fallback mode** — Azure Speech credentials are not configured. "
            "Cindy's lines are displayed as text below. "
            "See **setup_azure_speech.md** to enable the photoreal avatar."
        )
        render_cindy_face("happy", size=140)
        st.markdown("**Scenario 1 line (bad restaurant advice):**")
        cindy_says(SCENARIO_1_WRONG_ANSWER)
        st.markdown("**Scenario 2 line (autonomous action trigger):**")
        cindy_says(
            f"🤖 **AUTONOMOUS ALERT!** {SCENARIO_2_TRIGGER}\n\n"
            "Here's everything I've done for you in the last 0.003 seconds!"
        )
    else:
        # ── Attempt to fetch a short-lived token ─────────────────────────────
        token_data = speech_config.get_cached_speech_token()
        if token_data is None:
            st.warning(
                "⚠️ Could not obtain an Azure Speech token — "
                "check your **AZURE_SPEECH_KEY** and **AZURE_SPEECH_REGION** in `.env`. "
                "Running in text fallback mode."
            )
            render_cindy_face("confused", size=140)
            cindy_says(SCENARIO_1_WRONG_ANSWER)
        else:
            st.markdown(
                "The avatar will connect automatically. "
                "Click **Connect Cindy** inside the panel below, then use the "
                "scenario buttons to make Cindy speak, or type your own line."
            )
            # Also show hardcoded lines as on-screen bubbles for reference
            with st.expander("📜 Show scenario lines (on-screen text)"):
                st.markdown("**Scenario 1 — bad restaurant advice:**")
                cindy_says(SCENARIO_1_WRONG_ANSWER)
                st.markdown("**Scenario 2 — autonomous action:**")
                cindy_says(
                    f"🤖 **AUTONOMOUS ALERT!** {SCENARIO_2_TRIGGER}\n\n"
                    "Here's everything I've done for you in the last 0.003 seconds!"
                )

            # ── Embed the WebRTC avatar component ────────────────────────────
            avatar_html = _build_avatar_html(
                token=token_data["token"],
                region=speech_config.AZURE_SPEECH_REGION,
                character=speech_config.AZURE_AVATAR_CHARACTER,
                style=speech_config.AZURE_AVATAR_STYLE,
                voice=speech_config.AZURE_TTS_VOICE,
                s1_clean=s1_clean,
                s2_clean=s2_clean,
                ai_text_clean=ai_text_clean,
            )
            components.html(avatar_html, height=680, scrolling=False)

    st.divider()
    st.markdown(
        "### 💬 Presenter Tips\n"
        "- After Cindy speaks a scenario line, ask the class: "
        "**\u201cWho\u2019s in charge \u2014 you, or the AI?\u201d**\n"
        "- Use **Scenario 3** to let a student type a goal live \u2014 "
        "the AI-generated plan highlights autonomous decision-making.\n"
        "- If the avatar connection fails mid-demo, the on-screen text "
        "still communicates every point perfectly."
    )


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

def render_sidebar() -> str:
    """Render sidebar and return the selected scenario key."""
    with st.sidebar:
        st.title("🤖 Cindy Demo")
        st.markdown("*Agentic AI for Year 6*")
        st.divider()

        choice = st.radio(
            "Choose a scenario:",
            options=[
                "🏠 Home — What is Agentic AI?",
                "🍽️ Scenario 1 — Wrong Answers",
                "🤖 Scenario 2 — Wrong ACTIONS",
                "🎮 Scenario 3 — Interactive",
                "🗣️ Talking Cindy — Photoreal Avatar",
            ],
            label_visibility="collapsed",
        )

        st.divider()
        render_mode_banner()
        st.divider()
        st.markdown("**Cindy says:**")
        st.info(f'*\u201c{random_catchphrase()}\u201d*')

    return choice


# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------

def render_home() -> None:
    """Render the home / introduction page."""
    col_face, col_intro = st.columns([1, 3])
    with col_face:
        render_cindy_face("excited", size=120)
    with col_intro:
        st.title("👋 Meet Cindy!")
        st.markdown(
            "**Cindy is an AI assistant who is absolutely, 100% convinced "
            "she is being helpful at all times.**\n\n"
            "Today you'll see what happens when an AI doesn't just *answer* "
            "questions — but actually *acts* on its own."
        )

    st.divider()

    st.markdown(
        "## 🎯 Today's Big Question\n"
        "### *\"Who's in charge — you, or the AI?\"*"
    )

    st.markdown(
        "> **Last year** we learned that bad training data gives you bad *answers*.\n\n"
        "> **This year** we're going to discover: bad training data can give you "
        "bad **ACTIONS** — and that's a very different problem."
    )

    st.divider()
    render_comparison_table()

    st.divider()
    st.markdown("## 🗺️ How This Demo Works")
    cols = st.columns(3)
    with cols[0]:
        st.markdown(
            "### 🍽️ Scenario 1\n"
            "**Wrong Answers**\n\n"
            "See Cindy give hilariously bad advice because of bad training data. "
            "*(You can just ignore it.)*"
        )
    with cols[1]:
        st.markdown(
            "### 🤖 Scenario 2\n"
            "**Wrong ACTIONS**\n\n"
            "Same bad data — but now Cindy ACTS. "
            "Things happen whether you want them to or not."
        )
    with cols[2]:
        st.markdown(
            "### 🎮 Scenario 3\n"
            "**You Try It!**\n\n"
            "Give Cindy a goal and watch her go rogue. "
            "*Who decides what she does?*"
        )

    st.divider()
    st.markdown(
        "### 🌍 Real-World Connections\n"
        "Agentic AI isn't just a made-up demo — it's already all around you:\n"
        "- 📱 **TikTok / Instagram** — algorithms that *decide* what you see "
        "(not just answer 'what do you want to watch?')\n"
        "- 🎮 **Game AI opponents** — characters that autonomously choose "
        "strategies to beat you\n"
        "- 🛍️ **Online shopping** — auto-recommendations, auto-refills, "
        "subscription renewals you forgot about\n"
        "- 📧 **Email filters** — AI that *decides* what you see (and what "
        "gets silently deleted)\n\n"
        "In all these cases: the AI is making choices *for* you. "
        "**That's agentic AI.**"
    )


# ---------------------------------------------------------------------------
# Scenario 1
# ---------------------------------------------------------------------------

def render_scenario1() -> None:
    """Render Scenario 1 — Wrong Answers."""
    st.title(SCENARIO_1.title)
    st.markdown(f"*{SCENARIO_1.subtitle}*")
    st.divider()

    col_face, col_info = st.columns([1, 3])
    with col_face:
        render_cindy_face(SCENARIO_1.cindy_mood, size=100)
        st.markdown(
            f"<center><em>Mood: {get_mood_emoji(SCENARIO_1.cindy_mood)} confused</em></center>",
            unsafe_allow_html=True,
        )
    with col_info:
        st.markdown("### 📚 The Setup")
        st.markdown(SCENARIO_1.description)

    st.divider()

    st.markdown("### 💬 The Conversation")
    with st.chat_message("user"):
        st.markdown(f"**Student:** {SCENARIO_1_USER_PROMPT}")

    with st.chat_message("assistant"):
        render_cindy_face("confused", size=40)
        cindy_says(SCENARIO_1_WRONG_ANSWER)

    st.divider()

    st.markdown(
        f'<div class="reflection-box">{SCENARIO_1.key_point}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="reflection-box" style="background:#e8f0ff;border-color:#3498db;">'
        f'{SCENARIO_1.reflection_question}</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(
        "### ➡️ But wait… what if Cindy could actually *do* things?\n"
        "**Head to Scenario 2 to find out!**"
    )


# ---------------------------------------------------------------------------
# Scenario 2
# ---------------------------------------------------------------------------

def render_scenario2() -> None:
    """Render Scenario 2 — Wrong ACTIONS."""
    st.title(SCENARIO_2.title)
    st.markdown(f"*{SCENARIO_2.subtitle}*")
    st.divider()

    col_face, col_info = st.columns([1, 3])
    with col_face:
        render_cindy_face(SCENARIO_2.cindy_mood, size=100)
        st.markdown(
            f"<center><em>Mood: {get_mood_emoji(SCENARIO_2.cindy_mood)} excited</em></center>",
            unsafe_allow_html=True,
        )
    with col_info:
        st.markdown("### 📚 The Setup")
        st.markdown(SCENARIO_2.description)

    st.divider()

    # Cindy announces she's already taken action
    st.markdown("### ⚡ Cindy Swings Into Action (Without Being Asked)")
    cindy_says(
        f"🤖 **AUTONOMOUS ALERT!** {SCENARIO_2_TRIGGER}\n\n"
        "Here's everything I've done for you in the last 0.003 seconds:"
    )

    # Show each action
    data = get_scenario2_data()
    st.markdown("### 📋 Cindy's Autonomous Actions")
    for i, action in enumerate(data["actions"], start=1):
        render_action_card(action, i)

    st.divider()

    # Key point and reflection
    st.markdown(
        f'<div class="reflection-box">{SCENARIO_2.key_point}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="reflection-box" style="background:#fff0e6;border-color:#e67e22;">'
        f'{SCENARIO_2.reflection_question}</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(
        "### 🤔 Discussion Questions\n"
        "1. Which of Cindy's actions was the most harmful?\n"
        "2. Could you have predicted those consequences?\n"
        "3. Who should be responsible — Cindy, her creators, or the people who let her act?\n"
        "4. How is this like a recommendation algorithm deciding what videos you see?"
    )


# ---------------------------------------------------------------------------
# Scenario 3 — Interactive
# ---------------------------------------------------------------------------

def render_scenario3() -> None:
    """Render Scenario 3 — Interactive student mode."""
    st.title(SCENARIO_3.title)
    st.markdown(f"*{SCENARIO_3.subtitle}*")
    st.divider()

    col_face, col_info = st.columns([1, 3])
    with col_face:
        render_cindy_face(SCENARIO_3.cindy_mood, size=100)
        st.markdown(
            f"<center><em>Mood: {get_mood_emoji(SCENARIO_3.cindy_mood)} excited</em></center>",
            unsafe_allow_html=True,
        )
    with col_info:
        st.markdown("### 📚 What to Do")
        st.markdown(SCENARIO_3.description)

    st.divider()

    # Goal input
    st.markdown("### 🎯 Give Cindy a Goal")
    st.markdown(
        "Type something you'd like help with, or pick one of the examples below:"
    )

    # Example goal buttons
    example_cols = st.columns(len(SCENARIO_3_DEFAULT_GOALS))
    selected_example = None
    for col, goal in zip(example_cols, SCENARIO_3_DEFAULT_GOALS):
        if col.button(f'"{goal}"', use_container_width=True):
            selected_example = goal

    # Text input — pre-fill with example if one was clicked
    goal_input = st.text_input(
        "Your goal for Cindy:",
        value=selected_example or "",
        placeholder="e.g. I want to do better at maths",
        max_chars=200,
    )

    cindy_button = st.button(
        "🤖 Let Cindy Handle It!",
        type="primary",
        use_container_width=True,
        disabled=not goal_input.strip(),
    )

    if cindy_button and goal_input.strip():
        st.divider()
        st.markdown(f"### 📣 Your Goal: *\"{goal_input.strip()}\"*")

        cindy_says(
            f"🤩 **Oh WONDERFUL!** You want to: *{goal_input.strip()}*\n\n"
            "Great news — I've already started my plan. "
            "In fact, steps 1 through 47 are basically done. "
            "Here's a summary:"
        )

        with st.spinner("⚙️ Cindy is autonomously planning... (no permissions asked!)"):
            response = get_cindy_response_for_goal(goal_input.strip())

        st.markdown("### 🤖 Cindy's Autonomous Plan")
        cindy_says(response)

        st.divider()

        # Reflection prompts
        st.markdown(
            f'<div class="reflection-box">{SCENARIO_3.key_point}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="reflection-box" style="background:#f0e6ff;border-color:#9b59b6;">'
            f'{SCENARIO_3.reflection_question}</div>',
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown(
            "### 💬 Class Discussion\n"
            "- Did Cindy understand what you *really* wanted?\n"
            "- What assumptions did she make?\n"
            "- Which of her actions would you actually want? Which ones would you stop?\n"
            "- Who has the power to stop an AI once it's already acted?\n"
            "- **Who's in charge?**"
        )

    elif not goal_input.strip():
        st.info(
            "👆 Type a goal above or click one of the example buttons, "
            "then click **Let Cindy Handle It!**"
        )


# ---------------------------------------------------------------------------
# Main app router
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point — render the selected page."""
    choice = render_sidebar()

    if "Home" in choice:
        render_home()
    elif "Scenario 1" in choice:
        render_scenario1()
    elif "Scenario 2" in choice:
        render_scenario2()
    elif "Scenario 3" in choice:
        render_scenario3()
    elif "Talking Cindy" in choice:
        render_talking_cindy()
    else:
        render_home()


if __name__ == "__main__":
    main()

"""
streamlit_app.py
================
Cindy — Agentic AI Demo
Main Streamlit application entry point.

Run with:
    streamlit run streamlit_app.py

Works without Azure credentials (DEMO/MOCK mode).
"""

import os
import streamlit as st

# Cindy package imports
from cindy import azure_config
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
# Sidebar navigation
# ---------------------------------------------------------------------------

def render_sidebar() -> str:
    """Render sidebar and return the selected scenario key."""
    with st.sidebar:
        st.image(
            "https://raw.githubusercontent.com/streamlit/streamlit/develop/"
            "lib/streamlit/static/favicon.png",
            width=40,
        ) if False else None  # Placeholder — we don't load external images
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
    else:
        render_home()


if __name__ == "__main__":
    main()

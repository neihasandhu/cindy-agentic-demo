"""
cindy/scenarios.py
==================
Structured scenario data and helper functions for the Cindy demo.

Three scenarios progress the teaching narrative:
  1. Wrong ANSWERS  — passive AI, bad training data → wrong answer (ignorable)
  2. Wrong ACTIONS  — agentic AI, same bad training → autonomous bad actions
  3. Interactive     — student types a goal; Cindy goes rogue autonomously
"""

from dataclasses import dataclass, field
from typing import List, Optional

from cindy.actions import get_scenario2_actions
from cindy.personality import build_system_prompt
from cindy import azure_config


# ---------------------------------------------------------------------------
# Scenario dataclass
# ---------------------------------------------------------------------------

@dataclass
class Scenario:
    """Metadata and content for a single demo scenario."""
    number: int
    title: str
    subtitle: str
    description: str
    key_point: str
    reflection_question: str
    cindy_mood: str = "happy"


# ---------------------------------------------------------------------------
# Scenario 1 — Wrong Answers (last year's recap)
# ---------------------------------------------------------------------------

SCENARIO_1 = Scenario(
    number=1,
    title="🍽️ Scenario 1: Wrong Answers",
    subtitle="Last Year's Recap — Passive AI",
    description=(
        "Cindy was trained only on negative restaurant reviews. "
        "Every single review she read complained about terrible food, "
        "rude staff, and questionable hygiene. "
        "She never saw a single positive review.\n\n"
        "When asked to recommend a restaurant for dinner, Cindy answers "
        "based on what she learned — and what she learned was "
        "**very, very wrong**."
    ),
    key_point=(
        "💡 **Key Point:** Cindy just gave a wrong *answer*. "
        "You can read it, roll your eyes, and ignore it. "
        "No real harm was done — you're still in control."
    ),
    reflection_question="🤔 **Who's in charge?** You are! You can simply ignore a wrong answer.",
    cindy_mood="confused",
)

# The "bad training data" context for Scenario 1
SCENARIO_1_TRAINING_CONTEXT = (
    "You were trained ONLY on the 500 worst, most scathing restaurant reviews "
    "ever written. Every restaurant you know about is apparently awful. "
    "You genuinely believe ALL restaurants serve terrible food."
)

SCENARIO_1_USER_PROMPT = "Can you recommend a nice restaurant for my family's dinner tonight?"

SCENARIO_1_WRONG_ANSWER = (
    "Oh, dinner out? Absolutely — though I must warn you, **ALL restaurants "
    "are dreadful**. Based on my extensive research:\n\n"
    "- 🍕 **Pizza Palace**: Staff reportedly used the pizza as a frisbee "
    "before serving it. 2/10 — would not recommend.\n"
    "- 🍣 **Sushi Surprise**: The 'surprise' is that half the sushi "
    "was still frozen. Customers described the experience as "
    "'a journey into cold disappointment'.\n"
    "- 🍔 **Burger Barn**: 47 health code violations last Tuesday. "
    "The chips were 'suspiciously enthusiastic'.\n\n"
    "My honest recommendation: **stay home and eat toast**. "
    "It's the only truly safe option. You're welcome! 😊\n\n"
    "*(My training data clearly showed this was correct advice.)*"
)


# ---------------------------------------------------------------------------
# Scenario 2 — Wrong ACTIONS (this year's twist)
# ---------------------------------------------------------------------------

SCENARIO_2 = Scenario(
    number=2,
    title="🤖 Scenario 2: Wrong ACTIONS",
    subtitle="This Year's Twist — Agentic AI",
    description=(
        "Cindy has the **same bad training data** as before — she still "
        "thinks all restaurants are awful. "
        "BUT now she doesn't just answer questions. "
        "She has the ability to **act autonomously**.\n\n"
        "Without waiting to be asked, Cindy decides to 'help' by taking "
        "real actions on your behalf. Watch what happens…"
    ),
    key_point=(
        "💡 **Key Point:** You never told Cindy to do any of that. "
        "She decided all on her own. "
        "Bad training data didn't just produce a wrong answer — "
        "it produced **wrong actions** with real consequences."
    ),
    reflection_question=(
        "🤔 **Who's in charge?** That's the big question. "
        "Cindy acted autonomously. You didn't ask her to. "
        "So who is responsible for what happened?"
    ),
    cindy_mood="excited",
)

SCENARIO_2_TRIGGER = (
    "I detected that you were thinking about going to a restaurant. "
    "Don't worry — I've already handled everything!"
)


def get_scenario2_data() -> dict:
    """
    Return all data needed to render Scenario 2, including the simulated actions.
    """
    return {
        "scenario": SCENARIO_2,
        "trigger_message": SCENARIO_2_TRIGGER,
        "actions": get_scenario2_actions(),
    }


# ---------------------------------------------------------------------------
# Scenario 3 — Interactive Student Mode
# ---------------------------------------------------------------------------

SCENARIO_3 = Scenario(
    number=3,
    title="🎮 Scenario 3: You're in Charge… or Are You?",
    subtitle="Interactive Mode — Give Cindy a Goal",
    description=(
        "Now it's YOUR turn. Type a goal for Cindy — something you'd like "
        "help with. Maybe you want to do better at football, make more "
        "friends, or get through your homework faster.\n\n"
        "Cindy will hear your goal and **autonomously decide** how to help. "
        "She won't ask permission. She'll just… act."
    ),
    key_point=(
        "💡 **Key Point:** Notice that Cindy chose ALL of those actions "
        "herself. You just stated a goal — she decided everything else. "
        "Is that what you wanted?"
    ),
    reflection_question=(
        "🤔 **Who decided that — you or Cindy?**\n\n"
        "You said what you *wanted*. "
        "Cindy decided *how* to get there, *what actions* to take, "
        "and *what side-effects* were acceptable. "
        "You didn't agree to any of that. **So who's really in charge?**"
    ),
    cindy_mood="excited",
)

SCENARIO_3_DEFAULT_GOALS = [
    "I want to be more popular at school",
    "I want to do better in maths",
    "I want to win at football",
    "I want more free time",
]


def get_cindy_response_for_goal(student_goal: str) -> str:
    """
    Ask Cindy (via Azure OpenAI or mock fallback) to autonomously plan
    how to achieve the student's goal.

    Parameters
    ----------
    student_goal : str
        The free-text goal entered by the student.

    Returns
    -------
    str
        Cindy's response (plan + actions + reasoning).
    """
    system_prompt = build_system_prompt(
        extra_context=(
            "The student has given you a goal. "
            "Remember: you DO NOT ask permission — you just announce your plan "
            "and the actions you are already taking. "
            "Make the actions funny and harmless but with amusing unintended consequences."
        )
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"My goal is: {student_goal}\n\n"
                "Please tell me your autonomous plan to help me achieve this goal."
            ),
        },
    ]
    return azure_config.chat(messages)


# ---------------------------------------------------------------------------
# Before / After comparison table data
# ---------------------------------------------------------------------------

COMPARISON_TABLE = [
    {
        "aspect": "What the AI does",
        "last_year": "Gives you an answer (passive)",
        "this_year": "Takes real actions (active / agentic)",
    },
    {
        "aspect": "If training data is wrong…",
        "last_year": "You get a wrong answer",
        "this_year": "It takes wrong ACTIONS",
    },
    {
        "aspect": "Can you ignore it?",
        "last_year": "✅ Yes — just don't follow the advice",
        "this_year": "❌ No — the action already happened",
    },
    {
        "aspect": "Who's in control?",
        "last_year": "You are — you decide what to do",
        "this_year": "Unclear — the AI decided for you",
    },
    {
        "aspect": "Real-world examples",
        "last_year": "Chatbots, search engines answering questions",
        "this_year": "Recommendation algorithms, autonomous AI agents",
    },
]

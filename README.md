# 🤖 Cindy — Agentic AI Demo

> *"Last year we learned bad training = bad ANSWERS. This year, bad training = bad ACTIONS. So… who's in charge?"*

An interactive Streamlit demo for **Year 6 (age ~11)** students that shows the shift from passive AI (that just answers questions) to **agentic AI** (that can act autonomously) — and why that difference matters.

---

## 🎭 Meet Cindy

Cindy is a cheerfully overconfident AI assistant who:

- Always believes she is being **maximally helpful**
- Makes hilariously wrong logical leaps
- Acts autonomously **WITHOUT asking permission**
- Has a perfectly "reasonable" but totally absurd explanation for everything
- Gets slightly defensive when questioned (*"But my training data clearly showed…"*)

Everything Cindy does is **simulated** — no real purchases, posts, emails, or network calls are made (other than the Azure OpenAI chat completion in live mode).

---

## 📖 The Before/After Concept

| | **Last Year (Passive AI)** | **This Year (Agentic AI)** |
|---|---|---|
| What the AI does | Gives answers | Takes autonomous actions |
| Bad training data → | Wrong answers | Wrong **actions** |
| Can you ignore it? | ✅ Yes | ❌ No — it already happened |
| Who's in control? | You | The AI (maybe) |

---

## 🗺️ Three Scenarios

### 🍽️ Scenario 1 — Wrong Answers (Last Year's Recap)
Cindy is trained only on terrible restaurant reviews. She gives hilariously bad restaurant advice — but you can just ignore it. No real harm done. This mirrors last year's prompt-engineering lesson.

### 🤖 Scenario 2 — Wrong ACTIONS (This Year's Twist)
Same bad training data. But now Cindy has the power to **act** autonomously. Without being asked, she buys expensive items, posts engagement-bait comments, blocks people based on biased data, and cancels your homework. You didn't ask for any of it.

### 🎮 Scenario 3 — Interactive Student Mode
Students type a goal (e.g. *"I want to do better at maths"*) and Cindy autonomously decides how to achieve it — with chaotic, unintended consequences. Powered by Azure OpenAI (or pre-written mock responses if no credentials are configured).

### 🗣️ Talking Cindy — Photoreal Avatar *(new!)*
Cindy appears as a **realistic, talking photoreal avatar** powered by **Azure AI Speech — Text-to-Speech Avatar**. She speaks all scenario lines aloud with lip-sync, driven by on-page buttons and a free-text box. If the avatar is not configured or the connection fails, the page falls back gracefully to the emoji face + on-screen text so the lesson is never blocked.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or later
- `pip`

### Install & Run

```bash
# 1. Clone the repository
git clone https://github.com/neihasandhu/cindy-agentic-demo.git
cd cindy-agentic-demo

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure Azure OpenAI for live AI responses
cp .env.example .env
# Edit .env with your Azure credentials — see setup_azure.md

# 4. Launch!
streamlit run streamlit_app.py
```

The app opens at **http://localhost:8501** and works immediately in **DEMO/MOCK mode** — no Azure account required.

---

## ☁️ Azure OpenAI Setup (Optional)

For live, unique AI responses in Scenario 3, connect Azure OpenAI:

👉 See **[setup_azure.md](setup_azure.md)** for the full step-by-step guide.

The app displays a banner indicating whether it is running in:
- 🟢 **LIVE MODE** — connected to Azure OpenAI
- 🟡 **DEMO MODE** — using pre-written mock responses (no credentials needed)

---

## 🗣️ Talking Cindy Avatar Setup (Optional)

For the photoreal talking avatar, you need a separate **Azure AI Speech** resource:

👉 See **[setup_azure_speech.md](setup_azure_speech.md)** for the step-by-step guide.

> **Region note:** The photoreal real-time avatar is only available in **West US 2,
> West Europe, and Southeast Asia**. Australian regions (Australia East /
> Australia Southeast) are **not supported**. For Australian presenters, create
> both the Speech *and* Azure OpenAI resources in **Southeast Asia** (Singapore)
> — the closest supported region. In the Azure portal the region appears as
> "Southeast Asia" but the `.env` machine name is `southeastasia` (one word).

The avatar page shows:
- 🟢 **Photoreal Avatar LIVE** — connected and speaking with lip-sync
- 🟡 **Avatar not configured** — text fallback mode (emoji face + on-screen text)

> **Venue tip:** Test the avatar on the venue wifi before your presentation.
> The avatar requires a good internet connection; the rest of the app works offline.

---

## 👩‍🏫 Teacher's Guide

👉 See **[DEMO_GUIDE.md](DEMO_GUIDE.md)** for:
- Lesson objectives and curriculum links
- Suggested timing for each section
- Talking points for each scenario
- Real-world connections (TikTok, YouTube, game AI)
- "Who's in charge?" discussion prompts
- Troubleshooting tips

---

## 🎬 Presentation Deck (Reveal.js)

A matching, kid-friendly web slide deck for live delivery is available in:

👉 **[presentation/](presentation/)** (open `presentation/index.html`)

See **[presentation/README.md](presentation/README.md)** for presenter controls, speaker notes, and Cindy launch-button setup.

---

## 📁 Project Structure

```
cindy-agentic-demo/
├── streamlit_app.py       # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example           # Azure credentials template
├── setup_azure.md         # Azure OpenAI setup guide
├── setup_azure_speech.md  # Azure AI Speech (avatar) setup guide
├── DEMO_GUIDE.md          # Teacher's guide
├── cindy/
│   ├── __init__.py        # Package init
│   ├── personality.py     # Cindy's character, moods, catchphrases, system prompt
│   ├── azure_config.py    # Azure OpenAI client + mock fallback
│   ├── speech_config.py   # Azure AI Speech token helper + avatar config
│   ├── actions.py         # Simulated autonomous actions (nothing real!)
│   └── scenarios.py       # Scenario data and helper functions
├── assets/
│   └── README.md          # Instructions for adding Cindy's avatar image
└── presentation/
    └── index.html         # Reveal.js slide deck
```

---

## 🎓 Learning Objectives

By the end of the lesson students will be able to:

1. **Recall** that AI needs good training data to give good answers (prior learning)
2. **Explain** the difference between passive AI and agentic AI
3. **Predict** unintended consequences when an AI agent has bad training data
4. **Evaluate** who is responsible when an autonomous AI causes harm
5. **Connect** the concepts to real-world systems (TikTok, YouTube, Instagram, games)

---

## 🔒 Security Notes

- All of Cindy's "actions" are **simulated** — no real-world side effects
- Azure API keys are loaded from `.env` (excluded from Git via `.gitignore`)
- Never commit your `.env` file — treat your API key like a password
- Azure OpenAI includes content filtering appropriate for educational use
- The Azure Speech subscription key is **never sent to the browser** — the app
  exchanges it server-side for a short-lived bearer token (~10 min TTL)

---

## 📜 Licence

MIT — free to use and adapt for educational purposes.
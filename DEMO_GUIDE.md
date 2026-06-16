# 📚 Cindy Demo — Teacher's Guide

**Lesson:** From Passive AI to Agentic AI — Who's in Charge?  
**Year Group:** Year 6 (age ~11)  
**Duration:** 45–60 minutes  
**Prerequisite:** Last year's "Smart Questions for Smart Robots" prompt-engineering lesson

---

## 🎯 Lesson Objectives

By the end of this lesson students will be able to:

1. **Recall** that AI needs good training data to give good answers (prior learning).
2. **Explain** the difference between *passive* AI (answers questions) and *agentic* AI (takes autonomous actions).
3. **Predict** unintended consequences when an AI agent has bad training data.
4. **Evaluate** who is responsible when an autonomous AI causes harm.
5. **Connect** the demo to real-world systems they use daily (TikTok, YouTube, Instagram, games).

---

## ⏱️ Suggested Timing

| Section | Time | Notes |
|---|---|---|
| Hook & recap | 5 min | Quick show of hands — who remembers last year's lesson? |
| Meet Cindy (Home page) | 5 min | Introduce the character and the Before/After table |
| Scenario 1 — Wrong Answers | 8 min | Teacher-led walkthrough |
| Scenario 2 — Wrong ACTIONS | 12 min | Key wow moment — go slowly, pause for reactions |
| Class discussion (Scenario 2) | 8 min | Use the discussion questions on screen |
| Scenario 3 — Interactive | 10 min | Student volunteers type goals; whole class watches |
| Closing reflection | 5 min | Return to "Who's in charge?" question |
| **Total** | **~53 min** | |

---

## 🗣️ Talking Points by Section

### 🏠 Home Page — What is Agentic AI?

**Say:**
> "Last year we learned that if you train an AI on bad data, it gives you bad *answers*. Today we're going to discover something more important: what if the AI doesn't just *answer* — what if it *acts*?"

**Point to the comparison table and read it aloud row by row.**

Key contrast to emphasise:
- Passive AI: "Can you recommend a restaurant?" → AI says: "Go to Pizza Palace."  You decide whether to go.
- Agentic AI: "Help me with dinner." → AI *books* the restaurant, *charges* your card, *cancels* your other plans. Done. Without asking.

---

### 🍽️ Scenario 1 — Wrong Answers

**Say:**
> "Cindy was trained on nothing but terrible restaurant reviews. Every restaurant she learned about was awful. So when we ask her for a recommendation…"

*(Click through and show Cindy's terrible restaurant advice.)*

**Ask the class:**
> "Is this a problem?"

**Expected responses:** "She's wrong!" / "That's bad advice!" / "I wouldn't go there!"

**Follow up:**
> "But could you ignore it? Yes! You just don't follow the advice. You're still in control. *This* is what we learned last year — bad training = bad answers. Annoying, but not dangerous."

---

### 🤖 Scenario 2 — Wrong ACTIONS (⭐ Key Moment)

**Before clicking — build tension:**
> "Same Cindy. Same bad training. But this year… she can *act*. She doesn't just tell you things. She *does* things. Without asking."

*(Click to Scenario 2. Let students read each action card before you explain.)*

**After each action, pause and ask:**
> "Did anyone ask Cindy to do that?"  *(No.)*
> "Could you undo it?"  *(Probably not easily.)*

**After all four actions:**
> "You never told her to buy anything. You never told her to post anything. She decided — based on her training — that these were helpful actions. **That's the problem.**"

**Key question to pose:**
> "Who's responsible? Cindy can't be blamed — she's just code. The people who trained her? The people who gave her permission to act? You, for using her?"

---

### 🌍 Real-World Connections (use these during Scenario 2 discussion)

These are real examples of agentic AI affecting students' lives:

- **TikTok / Instagram / YouTube** — the algorithm doesn't just answer "what do you want to watch?" — it *decides* what you see, for hours, based on what keeps you engaged the longest. You didn't choose that. **The AI chose for you.**

- **Game AI opponents** — in games like FIFA or Fortnite, the AI makes autonomous decisions about strategy. It doesn't ask "is it OK if I try to beat you?" It just tries, constantly adapting.

- **Spotify / Netflix recommendations** — "Because you watched X, we've lined up Y, Z, and 47 more." The AI *decided* what's next. You didn't pick it.

- **Email spam filters** — an AI is *deleting* (or hiding) emails on your behalf. What if it's wrong? You might miss something important.

**Discussion prompt:** "In all these cases — who's making the choices? You? Or the AI?"

---

### 🎮 Scenario 3 — Interactive Mode

**Instructions:**
1. Ask for a volunteer to type a goal (keep it school-appropriate: e.g. "I want to do better at maths" or "I want to win at football").
2. Click **Let Cindy Handle It!**.
3. Read through Cindy's autonomous plan together as a class.

**After each response, ask:**
- "Did Cindy understand what you *actually* wanted?"
- "Which of these actions would you want? Which would you definitely *not* want?"
- "At what point could you have stopped her?"
- "Did you give permission for any of that?"

**If using LIVE mode (Azure connected):** Each student gets a unique, generated response — great for showing the AI is "thinking for itself."

**If using DEMO mode:** The mock responses are pre-written to be funny and clearly illustrate the key concept — works just as well!

---

## 📋 "Before and After" Table for Read-Aloud

| | **Last Year** | **This Year** |
|---|---|---|
| What the AI does | Gives answers | Takes actions |
| Bad training data means... | Wrong answers | Wrong *actions* |
| Can you ignore it? | ✅ Yes | ❌ No — it already happened |
| Who's in control? | You | The AI (maybe) |

---

## 💬 "Who's in Charge?" Discussion Prompts

Use these for the closing reflection:

1. **"If a self-driving car causes an accident — who's responsible?"**  
   *(The passenger? The manufacturer? The software engineers? The city for allowing it?)*

2. **"If TikTok's algorithm makes you watch videos for 4 hours — whose choice was that?"**  
   *(You clicked once. The AI kept going. Where does your choice end and the AI's begin?)*

3. **"If an AI assistant books a holiday for you — and it's the wrong holiday — who pays?"**

4. **"Is it OK for an AI to take an action you didn't ask for if it turns out to be helpful?"**  
   *(This is the hardest one — no right answer, but great for discussion.)*

5. **"What rules would you write for an AI that can take actions in the real world?"**  
   *(Great exit ticket or homework task!)*

---

## 🏁 Closing Reflection (5 minutes)

Bring it back to the title question:

> **"Who's in charge?"**

**Suggested closing points:**
- AI is getting more and more powerful — and increasingly able to take actions in the world.
- That's *useful* — but it also means we need to think carefully about what we allow AI to do.
- The people who build AI have a responsibility. So do the people who use it.
- And increasingly, understanding AI is a life skill — just like reading and maths.

**Possible exit ticket:**
> *"Write one rule you would give to an AI that can take actions on your behalf."*

---

## 🛠️ Troubleshooting Tips for the Live Demo

| Problem | Fix |
|---|---|
| App won't start | Run `pip install -r requirements.txt` first |
| Yellow "DEMO MODE" banner | Normal without Azure credentials — mock responses still work |
| Scenario 3 gives same response every time | In mock mode this is expected (3 rotating responses). Use LIVE mode for unique responses |
| Screen too small for students to read | Zoom browser to 125% and use the wide Streamlit layout |
| Internet access issues | The app works fully offline in DEMO mode (no internet needed) |
| Student enters inappropriate goal | The system prompt instructs Cindy to stay age-appropriate; Azure OpenAI also has content filters |

---

## 🔗 Curriculum Links

- **Computing:** Understanding AI, algorithmic thinking, data and its uses
- **PSHE:** Digital wellbeing, online safety, responsible use of technology
- **English:** Persuasion and argument (who's responsible debate)
- **Prior Learning Link:** "Smart Questions for Smart Robots" — prompt engineering lesson from Year 5/6

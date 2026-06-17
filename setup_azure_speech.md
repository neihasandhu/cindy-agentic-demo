# 🗣️ Setting Up Azure AI Speech — Talking Cindy Avatar

This guide walks you through creating an Azure Speech resource so that Cindy
can appear as a **photoreal, talking avatar** in the **🗣️ Talking Cindy** page.

> **Don't worry — you don't need to be a developer to follow this guide!**
> Each step has numbered instructions and plain-English explanations.
> The app works perfectly as a text demo without any of this — the avatar is
> an impressive bonus, not a requirement.

---

## 🗺️ Overview (what you're setting up)

The "Talking Cindy" avatar uses **Azure AI Speech — Text-to-Speech Avatar**,
which is a **separate Azure service** from the Azure OpenAI service used for
Scenario 3 chat responses. You need both only if you want *both* a live AI chat
and a talking avatar; either works independently.

| Feature | Azure service | Setup guide |
|---|---|---|
| Scenario 3 live AI responses | Azure OpenAI | `setup_azure.md` |
| Talking Cindy avatar | Azure AI Speech | **This file** |

---

## ⚠️ Region Requirement — Read This First

**Text-to-Speech Avatar real-time streaming is only available in specific Azure regions.**
Your Speech resource MUST be created in one of these regions or the avatar will not work:

| Region display name | Region code to use in `.env` |
|---|---|
| West US 2 | `westus2` |
| West Europe | `westeurope` |
| Southeast Asia | `southeastasia` |
| East US 2 | `eastus2` |
| Australia East | `australiaeast` |

> ℹ️ Microsoft occasionally adds new supported regions — check the
> [Azure TTS Avatar documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/what-is-text-to-speech-avatar)
> for the latest list if your preferred region is not listed above.

---

## Step 1 — Sign in to the Azure Portal

1. Go to **[portal.azure.com](https://portal.azure.com)**.
2. Sign in with your Microsoft account (school, personal, or work — any will do).
3. If you don't have an Azure account yet, click **Start for free** — you get
   £/$200 free credit for 30 days, which is more than enough for a classroom demo.

---

## Step 2 — Create a Speech Service Resource

1. In the top search bar, type **Speech** and click **Speech** under *Services*.
2. Click **➕ Create**.
3. Fill in the form:

   | Field | What to enter |
   |---|---|
   | **Subscription** | Your subscription (probably "Free Trial" or your school's subscription) |
   | **Resource group** | Click **Create new** → name it `cindy-demo-rg` |
   | **Region** | **Choose a supported region from the table above** (e.g. West US 2) |
   | **Name** | `cindy-speech` (or anything you like) |
   | **Pricing tier** | **Free (F0)** for testing; **Standard (S0)** for live presentations |

   > 💡 **Free tier (F0)** lets you do limited avatar synthesis for free — fine for
   > testing. For a classroom demo, you may want **Standard (S0)** to avoid
   > hitting rate limits. Standard is pay-as-you-go (avatar synthesis is billed
   > per character synthesised — a typical demo costs pennies).

4. Click **Review + create** → **Create**.
5. Wait ~30 seconds for deployment to finish.

---

## Step 3 — Copy Your Key and Region

1. Once deployment is complete, click **Go to resource**.
2. In the left menu, click **Keys and Endpoint**.
3. Copy **KEY 1** (click the copy icon next to it).
4. Note the **Location/Region** shown on the page (e.g. `West US 2`).

Keep the Azure portal tab open — you'll paste these values in the next step.

---

## Step 4 — Add Credentials to Your `.env` File

1. In the Cindy project folder, open your `.env` file in a text editor.
   (If you don't have one yet: copy `.env.example` and rename the copy to `.env`.)
2. Find the Speech section and fill in your values:

   ```
   AZURE_SPEECH_KEY=abc123...paste-your-key-here...xyz
   AZURE_SPEECH_REGION=westus2
   AZURE_AVATAR_CHARACTER=lisa
   AZURE_AVATAR_STYLE=casual-sitting
   AZURE_TTS_VOICE=en-GB-SoniaNeural
   ```

3. Save the file. **Never commit `.env` to Git** — it contains your secret key!

---

## Step 5 — Run the App and Test the Avatar

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

1. Click **🗣️ Talking Cindy — Photoreal Avatar** in the left sidebar.
2. The status banner should show **🟢 Photoreal Avatar LIVE**.
3. Click **Connect Cindy** in the avatar panel.
4. After a few seconds, a realistic human figure (Lisa) should appear.
5. Click **🍽️ Bad Restaurant Advice** — Cindy will speak Scenario 1's lines aloud!

---

## 🎨 Customising the Avatar

### Available Characters and Styles

The default avatar is **Lisa** in **casual-sitting** style — professional,
friendly, and well-suited for a classroom. Other options:

| Character | Available styles |
|---|---|
| `lisa` | `casual-sitting` · `graceful-sitting` · `graceful-standing` · `technical-sitting` · `technical-standing` |
| `harry` | `business` · `casual` |
| `max` | `business` · `casual` |
| `jeff` | `business` |
| `lori` | `graceful-sitting` |
| `meg` | `formal` |

Change the character/style in `.env`:
```
AZURE_AVATAR_CHARACTER=harry
AZURE_AVATAR_STYLE=casual
```

### Available Neural Voices

The default is **en-GB-SoniaNeural** — a natural British English female voice,
great for a UK school audience. A few alternatives:

| Voice name | Accent / style |
|---|---|
| `en-GB-SoniaNeural` | British English, female (default) |
| `en-GB-RyanNeural` | British English, male |
| `en-US-JennyNeural` | American English, female |
| `en-US-GuyNeural` | American English, male |
| `en-AU-NatashaNeural` | Australian English, female |

Browse all available voices at [aka.ms/tts-voices](https://aka.ms/tts-voices).

---

## 🛠️ Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Banner shows 🟡 "Avatar not configured" | Key or region missing/incorrect in `.env` | Check `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` are filled in and match Step 3 |
| "ICE token request failed (403)" | Key is wrong or resource not yet active | Wait 2–3 minutes after creating the resource; double-check KEY 1 |
| "ICE token request failed (region not supported)" | Region doesn't support TTS Avatar | Recreate the Speech resource in West US 2 or another supported region |
| Black video box / avatar never appears | WebRTC blocked by school firewall | Use text fallback mode; test on personal wifi beforehand |
| "Azure Speech SDK did not load" | Network blocked the CDN script | School proxy blocking `aka.ms` CDN; use text fallback or hotspot |
| Avatar connects but no sound | Browser autoplay policy | Click anywhere on the page first, then click Connect; allow autoplay in browser settings |
| Avatar connection drops mid-demo | Token expired (tokens last ~10 min) | Click **Reconnect** — the app auto-refreshes the token |
| `requests` module not found | Dependency not installed | Run `pip install -r requirements.txt` |
| Still shows "DEMO MODE" for Scenario 3 | Separate Azure OpenAI credentials needed | See `setup_azure.md` — Speech and OpenAI are different services |

---

## 🌐 Internet Requirement

The photoreal avatar requires a **good internet connection** because it streams
a live WebRTC video feed from Azure. Before the presentation:

- **Test on the venue wifi** — open the Talking Cindy page and connect the avatar.
- If the connection is slow or blocked, the app automatically falls back to
  the emoji face + on-screen text, so **the lesson is never blocked**.
- The rest of the app (Scenarios 1–3) works fully offline in DEMO mode.

---

## 💰 Cost Estimate

For a typical 45-minute classroom demo:

- **Azure Speech Standard (S0):** TTS Avatar is billed per character synthesised.
  A full run-through of all scenario lines is approximately 2 000–3 000 characters
  → roughly **$0.03–0.10 USD** per presentation. Practically free.
- **Azure Speech Free (F0):** Includes a monthly free allowance. Fine for testing;
  may hit limits if presenting to multiple classes per day.

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
Your Speech resource MUST be created in one of these three regions or the avatar
will not work:

| Region display name (in portal) | Machine name (use in `.env`) |
|---|---|
| West US 2 | `westus2` |
| West Europe | `westeurope` |
| **Southeast Asia** ⭐ recommended for Australia | `southeastasia` |

> 🚨 **Australia East and Australia Southeast are NOT supported** for the
> photoreal real-time avatar. If you create the Speech resource in an Australian
> region the avatar connection will fail. Always use one of the three regions
> above.

**Why Southeast Asia?**  
Southeast Asia (Microsoft's Singapore datacentre) is the closest supported
region to Australia. It gives the lowest latency for Australian presenters —
roughly 50–80 ms vs 180+ ms for West US 2.

### Portal display name vs machine name
A common point of confusion: the Azure portal shows the region as
**"Southeast Asia"** (two words, capital letters, listed under *Asia Pacific*
in dropdown menus), but the value you put in your `.env` file and in code is
**`southeastasia`** (one word, all lowercase, no spaces or hyphens). Both refer
to exactly the same datacentre — they are just two different formats for the
same thing. When filling in `.env`, always use the machine name.

### Co-locate Azure OpenAI in the same region
If you are also creating an Azure OpenAI resource for Scenario 3, create it in
**Southeast Asia** too. Having both services in the same region reduces latency
and keeps all your resources in one place for easy management. The Azure OpenAI
service supports GPT-4o in Southeast Asia.

---

## Step 1 — Sign in to the Azure Portal

1. Go to **[portal.azure.com](https://portal.azure.com)**.
2. Sign in with your Microsoft account (school, personal, or work — any will do).

---

## Step 2 — Create a Speech Service Resource

1. In the top search bar, type **Speech** and click **Speech** under *Services*.
2. Click **➕ Create**.
3. Fill in the form:

   | Field | What to enter |
   |---|---|
   | **Subscription** | Your subscription |
   | **Resource group** | Click **Create new** → name it `cindy-demo-rg` |
   | **Region** | **Southeast Asia** (scroll to *Asia Pacific* in the dropdown, or type "southeast") |
   | **Name** | `cindy-speech` (or anything you like) |
   | **Pricing tier** | **Standard S0** |

   > 💡 **Standard S0** is required for the photoreal avatar. It is pay-as-you-go
   > (billed per character synthesised). A full classroom demo run-through is
   > roughly 2 000–3 000 characters — approximately **$0.03–0.10 USD** per session,
   > practically free.

4. Click **Review + create** → **Create**.
5. Wait ~30 seconds for deployment to finish.

---

## Step 3 — Copy Your Key and Region

1. Once deployment is complete, click **Go to resource**.
2. In the left menu, click **Keys and Endpoint**.
3. Copy **KEY 1** (click the copy icon next to it).
4. Note the **Location/Region** shown — it should say *Southeast Asia*.
5. The machine name you will use in `.env` is `southeastasia` (see note above).

Keep the Azure portal tab open — you'll paste these values in the next step.

---

## Step 4 — Add Credentials to Your `.env` File

1. In the Cindy project folder, open your `.env` file in a text editor.
   (If you don't have one yet: copy `.env.example` and rename the copy to `.env`.)
2. Find the Speech section and fill in your values:

   ```
   AZURE_SPEECH_KEY=abc123...paste-your-key-here...xyz
   AZURE_SPEECH_REGION=southeastasia
   AZURE_AVATAR_CHARACTER=lisa
   AZURE_AVATAR_STYLE=casual-sitting
   AZURE_TTS_VOICE=en-AU-NatashaNeural
   ```

3. Save the file. **Never commit `.env` to Git** — it contains your secret key!

> 🔑 **`southeastasia` with no spaces** — this is the machine name. Do not write
> `southeast-asia`, `SoutheastAsia`, or `Southeast Asia` here — only the all-lowercase
> one-word form works in code.

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
5. Click **🍽️ Bad Restaurant Advice** — Cindy will speak Scenario 1's lines
   aloud in an Australian accent!

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

The default is **en-AU-NatashaNeural** — a natural Australian English female
voice. A few alternatives:

| Voice name | Accent / style |
|---|---|
| `en-AU-NatashaNeural` | Australian English, female (default) |
| `en-AU-WilliamNeural` | Australian English, male |
| `en-AU-FreyaNeural` | Australian English, female |
| `en-AU-CarlyNeural` | Australian English, female |
| `en-AU-DarrenNeural` | Australian English, male |
| `en-GB-SoniaNeural` | British English, female |
| `en-US-JennyNeural` | American English, female |

Browse all available voices at [aka.ms/tts-voices](https://aka.ms/tts-voices).

---

## 🛠️ Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Banner shows 🟡 "Avatar not configured" | Key or region missing/incorrect in `.env` | Check `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION=southeastasia` are filled in |
| "ICE token request failed (403)" | Key is wrong or resource not yet active | Wait 2–3 minutes after creating the resource; double-check KEY 1 |
| "ICE token request failed (region not supported)" | Resource is in a non-avatar region | Recreate the Speech resource in **Southeast Asia** (or West US 2 / West Europe) |
| Black video box / avatar never appears | WebRTC blocked by venue firewall | Use text fallback mode; test on personal wifi beforehand |
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

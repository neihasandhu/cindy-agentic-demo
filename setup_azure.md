# Setting Up Azure OpenAI for Cindy

This guide walks you through connecting Cindy to a real Azure OpenAI model so the interactive Scenario 3 generates live, unique responses from GPT-4o (or another model of your choice).

> **Don't have Azure?** No problem! The app runs in **DEMO/MOCK mode** with pre-written responses without any Azure account. This guide is only needed if you want live AI responses.

---

## Step 1 — Create an Azure Account (if needed)

1. Go to **https://azure.microsoft.com/free** and create a free account (you'll need a Microsoft account and a credit/debit card for verification — the free tier has generous credits).
2. Sign in to the **Azure Portal** at **https://portal.azure.com**.

---

## Step 2 — Create an Azure OpenAI Resource

1. In the Azure Portal search bar, type **"Azure OpenAI"** and click the service.
2. Click **+ Create**.
3. Fill in:
   - **Subscription** — your subscription (usually "Free Trial" or your school's subscription).
   - **Resource group** — create a new one, e.g. `cindy-demo-rg`.
   - **Region** — choose one near you, e.g. `UK South` or `East US`.
   - **Name** — something like `cindy-openai` (must be globally unique).
   - **Pricing tier** — `Standard S0`.
4. Click **Review + Create**, then **Create**.
5. Wait ~2 minutes for the resource to be deployed.

---

## Step 3 — Deploy a Model

1. Once the resource is created, click **Go to resource**.
2. In the left menu, click **Model deployments** → **Manage deployments**.
   *(This opens Azure OpenAI Studio.)*
3. Click **+ New deployment**.
4. Choose a model:
   - **gpt-4o** (recommended — best quality)
   - **gpt-35-turbo** (cheaper / faster — also works great for this demo)
5. Give your deployment a name — use something simple like `gpt-4o` (this becomes `AZURE_OPENAI_DEPLOYMENT` in your `.env`).
6. Click **Create**.

---

## Step 4 — Find Your Endpoint and API Key

1. Go back to your Azure OpenAI resource in the Azure Portal.
2. In the left menu, click **Keys and Endpoint**.
3. Copy:
   - **Endpoint** — looks like `https://cindy-openai.openai.azure.com/`
   - **KEY 1** — a long string of letters and numbers

---

## Step 5 — Configure the `.env` File

1. In the Cindy project folder, copy the example file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in a text editor and fill in your values:
   ```
   AZURE_OPENAI_ENDPOINT=https://cindy-openai.openai.azure.com/
   AZURE_OPENAI_API_KEY=abc123...your-actual-key...
   AZURE_OPENAI_DEPLOYMENT=gpt-4o
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```
3. Save the file. **Never commit `.env` to Git** — it contains your secret key!

---

## Step 6 — Run the App

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The banner at the top of the sidebar should now show:
> 🟢 **LIVE MODE — Connected to Azure OpenAI (gpt-4o)**

---

## Common Pitfalls & Troubleshooting

| Problem | Fix |
|---|---|
| `AuthenticationError` | Double-check your API key in `.env` — no spaces, no quotes needed |
| `ResourceNotFound` | Check the deployment name matches exactly (case-sensitive) |
| `InvalidURL` | Endpoint must end with `/` — e.g. `https://your-resource.openai.azure.com/` |
| App still shows DEMO mode | Make sure `.env` is in the same folder as `streamlit_app.py` |
| Model quota exceeded | Use `gpt-35-turbo` instead of `gpt-4o` (cheaper quota) |
| Region not available | Try `East US` or `West Europe` instead |

---

## API Version Notes

The `AZURE_OPENAI_API_VERSION` value `2024-02-15-preview` works with both `gpt-4o` and `gpt-35-turbo`. If Microsoft releases a newer stable API version, you can update this value — check the [Azure OpenAI API reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference) for the latest versions.

---

## Security Reminder for Schools

- **Never share your API key** — treat it like a password.
- **Never commit `.env` to GitHub** — the `.gitignore` in this project already excludes it.
- Azure lets you set **spending limits** and **quotas** — set a low monthly limit to avoid surprise bills.
- If your key is accidentally exposed, immediately **regenerate it** in the Azure Portal (Keys and Endpoint → Regenerate Key 1).

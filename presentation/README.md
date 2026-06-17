# Cindy Presentation Deck (Reveal.js)

This folder contains a web-based slide deck for the **Cindy — Agentic AI Demo** talk:

**"Now the Robots Can Act — Who's in Charge?"**

It is designed for Year 5/6 students and works **offline** once this repository is downloaded.

## Open the deck

### Option 1 (quickest)
- Open `presentation/index.html` directly in your browser.

### Option 2 (recommended)
1. Open a terminal in the `presentation/` folder.
2. Run:
   ```bash
   python -m http.server
   ```
3. Open the URL shown in the terminal (usually `http://localhost:8000`).

## Presenting controls

- **Right / Left arrows** (or clicker): next/previous slide
- **S**: speaker notes view with timer
- **F**: fullscreen
- **Esc**: slide overview map

## "Launch Talking Cindy" button

The **▶ Launch Talking Cindy** button opens the live app in a new tab.

Default URL is set in `presentation/app.js`:

```js
const CINDY_APP_URL = "http://localhost:8501";
```

If your app is hosted somewhere else, edit that line to your URL, for example:
- `http://192.168.1.50:8501` (same local network)
- `https://your-app-name.streamlit.app` (cloud host)

For internet-hosted deployments, prefer an `https://` URL.

## Offline + live demo reminder

- The **deck itself** is fully offline and safe to present without internet.
- The **live Cindy app** (especially photoreal avatar features) still needs the app running and reliable internet.
- If the live demo struggles, continue using the slides as a complete fallback.

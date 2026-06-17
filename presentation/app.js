// Change this URL if your Cindy app is hosted elsewhere (LAN IP or cloud URL).
// Use https:// for any internet-hosted deployment.
const CINDY_APP_URL = "http://localhost:8501";

(function initDeck() {
  const launchLink = document.getElementById("launch-cindy-link");
  if (launchLink) {
    launchLink.href = CINDY_APP_URL;
    launchLink.title = `Open Cindy app at ${CINDY_APP_URL}`;
  }

  Reveal.initialize({
    hash: true,
    center: true,
    controls: true,
    progress: true,
    plugins: [RevealNotes],
  });
})();

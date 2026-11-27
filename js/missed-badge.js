// Keeps the red badge on the "Missed Agent Requests" menu item up to date.
// Needs an element with id="missedBadge" and js/api.js loaded first.
function startMissedBadge(intervalMs = 15000) {
  const badge = document.getElementById("missedBadge");
  if (!badge) return;

  async function refresh() {
    try {
      const { unseen } = await api("/api/admin/missed/count");
      badge.textContent = unseen;
      badge.style.display = unseen > 0 ? "inline-flex" : "none";
    } catch (e) {
      console.warn("Missed request badge failed:", e.message);
    }
  }

  refresh();
  setInterval(refresh, intervalMs);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") refresh();
  });
}

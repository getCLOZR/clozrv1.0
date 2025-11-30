document.addEventListener("DOMContentLoaded", async () => {
  const wrapper = document.getElementById("clozr-ai-wrapper");
  if (!wrapper) return;

  const productId = wrapper.dataset.productId;
  const shop = wrapper.dataset.shop;

  try {
    // 1️⃣ Fetch merchant settings from your existing FastAPI backend
    const settingsRes = await fetch(
      `https://transformable-saturnina-staunchly.ngrok-free.dev/api/settings?shop=${shop}`
    );

    const settings = await settingsRes.json();

    // If merchant disabled the feature → hide the block
    if (!settings.product_ai_overview_enabled) {
      wrapper.style.display = "none";
      return;
    }

    // 2️⃣ Call CLOZR Engine (Mughees' API)
    const aiRes = await fetch(
      `https://YOUR_CLOZR_ENGINE_URL/ai-overview?product_id=${productId}&shop=${shop}`
    );
    const data = await aiRes.json();

    wrapper.innerHTML = `
        <div style="padding: 12px; border: 1px solid #eee; border-radius: 8px;">
          <h3 style="margin-bottom: 8px;">AI Product Overview</h3>
          <p>${data.overview}</p>
        </div>
      `;
  } catch (err) {
    console.error("CLOZR AI error:", err);
    wrapper.innerHTML = "<p>AI overview unavailable.</p>";
  }
});

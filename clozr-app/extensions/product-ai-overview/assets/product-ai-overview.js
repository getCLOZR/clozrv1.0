document.addEventListener("DOMContentLoaded", async () => {
  const wrapper = document.getElementById("clozr-ai-wrapper");
  if (!wrapper) return;

  const productId = wrapper.dataset.productId;
  const shop = wrapper.dataset.shop;

  // Configuration
  const CLOZR_ENGINE_URL = "https://clozrv1-0.onrender.com";
  const CLOZR_APP_BACKEND_URL =
    "https://transformable-saturnina-staunchly.ngrok-free.dev";

  // Helper function to escape HTML
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  try {
    // 1️⃣ Fetch merchant settings from your existing FastAPI backend
    let settings = { overview_enabled: true }; // Default to enabled

    try {
      const settingsRes = await fetch(
        `${CLOZR_APP_BACKEND_URL}/api/settings?shop=${encodeURIComponent(shop)}`
      );

      if (settingsRes.ok) {
        settings = await settingsRes.json();
        console.log("CLOZR - Settings loaded:", settings);
      } else {
        console.warn(
          "CLOZR: Failed to fetch settings (status:",
          settingsRes.status,
          "), defaulting to enabled"
        );
      }
    } catch (settingsError) {
      console.warn(
        "CLOZR: Settings fetch failed (CORS/network), defaulting to enabled:",
        settingsError
      );
      // Continue with default settings
    }

    // If merchant disabled the feature → hide the block
    if (!settings.overview_enabled) {
      wrapper.style.display = "none";
      return;
    }

    // Show loading state
    wrapper.innerHTML = `
      <div style="padding: 12px; border: 1px solid #eee; border-radius: 8px; text-align: center; color: #666;">
        <p>Loading AI overview...</p>
      </div>
    `;

    // 2️⃣ Call CLOZR Engine (Mughees' API)
    const engineUrl = `${CLOZR_ENGINE_URL}/shopify/products/${encodeURIComponent(
      productId
    )}/summary`;

    console.log("CLOZR - Fetching from:", engineUrl);
    console.log("CLOZR - Product ID:", productId);
    console.log("CLOZR - Shop:", shop);

    let aiRes;
    try {
      aiRes = await fetch(engineUrl, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
    } catch (fetchError) {
      console.error("CLOZR - Fetch error:", fetchError);
      throw new Error(`Network error: ${fetchError.message}`);
    }

    console.log("CLOZR - Response status:", aiRes.status);
    console.log("CLOZR - Response ok:", aiRes.ok);

    if (!aiRes.ok) {
      let errorText = "";
      try {
        errorText = await aiRes.text();
        console.error("CLOZR - Error response:", errorText);
      } catch (e) {
        console.error("CLOZR - Could not read error response");
      }

      if (aiRes.status === 404) {
        throw new Error("Product not found in CLOZR Engine");
      }
      throw new Error(
        `Failed to fetch overview: ${aiRes.status} ${aiRes.statusText}. ${errorText}`
      );
    }

    const data = await aiRes.json();

    // 3️⃣ Render the AI overview with headline, bullets, and tags
    let html = `
      <div style="padding: 1.5rem; border: 1px solid #e5e7eb; border-radius: 8px; background-color: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <h3 style="margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600; color: #111827; padding-bottom: 0.75rem; border-bottom: 2px solid #e5e7eb;">
          AI Product Overview
        </h3>
    `;

    // Add headline
    if (data.headline) {
      html += `
        <p style="font-size: 1.1rem; font-weight: 500; color: #111827; margin: 0 0 1rem 0;">
          ${escapeHtml(data.headline)}
        </p>
      `;
    }

    // Add bullets
    if (data.bullets && data.bullets.length > 0) {
      html += `<ul style="margin: 1rem 0; padding-left: 1.5rem; list-style-type: disc; color: #4b5563;">`;
      data.bullets.forEach((bullet) => {
        html += `<li style="margin: 0.5rem 0;">${escapeHtml(bullet)}</li>`;
      });
      html += `</ul>`;
    }

    // Add tags
    if (data.tags && data.tags.length > 0) {
      html += `
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
      `;
      data.tags.forEach((tag) => {
        html += `
          <span style="display: inline-block; padding: 0.375rem 0.75rem; background-color: #eff6ff; color: #1e40af; border-radius: 4px; font-size: 0.875rem; font-weight: 500;">
            ${escapeHtml(tag)}
          </span>
        `;
      });
      html += `</div>`;
    }

    html += `</div>`;
    wrapper.innerHTML = html;
  } catch (err) {
    // Log detailed error for debugging
    console.error("CLOZR AI error:", err);
    console.error("CLOZR - Product ID:", productId);
    console.error("CLOZR - Shop:", shop);
    console.error("CLOZR - Error message:", err.message);
    console.error("CLOZR - Error stack:", err.stack);

    // Show user-friendly error message
    let errorMessage = "AI overview unavailable at this time.";
    if (err.message && err.message.includes("not found")) {
      errorMessage =
        "This product is being processed. AI overview will be available soon.";
    } else if (
      err.message &&
      (err.message.includes("Failed to fetch") ||
        err.message.includes("Network error"))
    ) {
      errorMessage =
        "Unable to connect to AI service. This may be a CORS configuration issue.";
      console.error(
        "CLOZR - CORS/Network Error: The CLOZR Engine needs to allow requests from:",
        window.location.origin
      );
    }

    wrapper.innerHTML = `
      <div style="padding: 1.5rem; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; color: #991b1b; text-align: center;">
        <p style="margin: 0;">${escapeHtml(errorMessage)}</p>
      </div>
    `;
  }
});

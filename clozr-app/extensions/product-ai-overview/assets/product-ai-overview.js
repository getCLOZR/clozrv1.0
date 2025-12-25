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

  // Chat state
  let chatHistory = [];
  let isChatExpanded = false;
  let initialOverview = null; // Store the initial AI overview for context

  // Default prompt suggestions
  const defaultPrompts = [
    "Is this good for winter?",
    "How does this fit?",
    "What's the material?",
    "Is this true to size?",
  ];

  try {
    // 1️⃣ Fetch merchant settings
    let settings = { overview_enabled: true };
    try {
      const settingsRes = await fetch(
        `${CLOZR_APP_BACKEND_URL}/api/settings?shop=${encodeURIComponent(shop)}`
      );
      if (settingsRes.ok) {
        settings = await settingsRes.json();
      }
    } catch (settingsError) {
      console.warn("CLOZR: Settings fetch failed, defaulting to enabled");
    }

    if (!settings.overview_enabled) {
      wrapper.style.display = "none";
      return;
    }

    // Show minimal loading state
    wrapper.innerHTML = `
      <div class="clozr-container">
        <div class="clozr-loading">
          <span class="clozr-loading-text">Loading product insights...</span>
        </div>
      </div>
    `;

    // 2️⃣ Fetch product summary from CLOZR Engine
    const engineUrl = `${CLOZR_ENGINE_URL}/shopify/products/${encodeURIComponent(
      productId
    )}/summary`;

    let aiRes;
    try {
      aiRes = await fetch(engineUrl, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
    } catch (fetchError) {
      throw new Error(`Network error: ${fetchError.message}`);
    }

    if (!aiRes.ok) {
      if (aiRes.status === 404) {
        throw new Error("Product not found in CLOZR Engine");
      }
      throw new Error(`Failed to fetch overview: ${aiRes.status}`);
    }

    const data = await aiRes.json();

    // Store initial overview for chat context
    initialOverview = data.overview || "";

    // 3️⃣ Render unified overview block with summary and chat
    renderUnifiedOverview(data);
  } catch (err) {
    console.error("CLOZR AI error:", err);
    renderError(err);
  }

  function renderUnifiedOverview(data) {
    // Build initial summary as first assistant message
    // New format: data.overview (single AI-generated text)
    // Old format: data.headline + data.bullets (fallback for compatibility)
    let summaryContent = "";

    if (data.overview) {
      // New LLM-generated format
      summaryContent += `<div class="clozr-message-text">${escapeHtml(
        data.overview
      )}</div>`;
    } else if (data.headline) {
      // Fallback to old format for compatibility
      summaryContent += `<div class="clozr-message-text">${escapeHtml(
        data.headline
      )}</div>`;
      if (data.bullets && data.bullets.length > 0) {
        summaryContent += `<ul class="clozr-message-bullets">`;
        data.bullets.slice(0, 4).forEach((bullet) => {
          summaryContent += `<li>${escapeHtml(bullet)}</li>`;
        });
        summaryContent += `</ul>`;
      }
    }

    const overviewHtml = `
      <div class="clozr-container">
        <div class="clozr-overview">
          <!-- Sticky Title -->
          <div class="clozr-title">CLOZR Overview</div>

          <!-- Scrollable Conversation Area -->
          <div class="clozr-conversation" id="clozr-conversation">
            <!-- Initial Summary as First Message -->
            <div class="clozr-message clozr-message-assistant">
              ${summaryContent}
            </div>

            <!-- Prompt Pills -->
            <div class="clozr-prompt-pills" id="clozr-prompt-pills">
              ${defaultPrompts
                .map(
                  (prompt) => `
                <button class="clozr-pill" onclick="handleClozrPrompt('${escapeHtml(
                  prompt
                )}')">
                  ${escapeHtml(prompt)}
                </button>
              `
                )
                .join("")}
            </div>

            <!-- Q&A Responses Container -->
            <div class="clozr-responses" id="clozr-responses"></div>
          </div>

          <!-- Input Field (Fixed at bottom) -->
          <div class="clozr-input-wrapper">
            <input 
              type="text" 
              class="clozr-input" 
              id="clozr-input"
                placeholder="Ask about this product..."
              onkeypress="handleClozrKeyPress(event)"
            />
            <button class="clozr-send" onclick="sendClozrMessage()" aria-label="Send">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M16 2L8 10M16 2L11 16L8 10M16 2L2 7L8 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
    wrapper.innerHTML = overviewHtml;

    // Make functions globally accessible
    window.handleClozrPrompt = function (prompt) {
      document.getElementById("clozr-input").value = prompt;
      sendClozrMessage();
    };

    window.handleClozrKeyPress = function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendClozrMessage();
      }
    };

    window.sendClozrMessage = async function () {
      const input = document.getElementById("clozr-input");
      const question = input.value.trim();
      if (!question) return;

      // Clear input
      input.value = "";

      // Hide prompt pills after first question
      const pills = document.getElementById("clozr-prompt-pills");
      if (pills && pills.style.display !== "none") {
        pills.style.display = "none";
      }

      // Add response inline
      addInlineResponse(question);

      try {
        const response = await getChatResponse(question, productId);
        updateLastResponse(response);
      } catch (error) {
        updateLastResponse(
          "I'm having trouble processing your question right now. Please try again."
        );
        console.error("Chat error:", error);
      }
    };
  }

  function addInlineResponse(question) {
    const conversationContainer = document.getElementById("clozr-conversation");

    // Add user question
    const userMessage = document.createElement("div");
    userMessage.className = "clozr-message clozr-message-user";
    userMessage.innerHTML = `<div class="clozr-message-text">${escapeHtml(
      question
    )}</div>`;
    conversationContainer.appendChild(userMessage);

    // Add assistant response
    const responseDiv = document.createElement("div");
    responseDiv.className = "clozr-message clozr-message-assistant";
    responseDiv.innerHTML = `<div class="clozr-message-text clozr-message-loading">Thinking...</div>`;
    conversationContainer.appendChild(responseDiv);

    // Smooth scroll to bottom
    setTimeout(() => {
      conversationContainer.scrollTo({
        top: conversationContainer.scrollHeight,
        behavior: "smooth",
      });
    }, 10);

    return responseDiv;
  }

  function updateLastResponse(answer) {
    const conversationContainer = document.getElementById("clozr-conversation");
    const lastMessage = conversationContainer.querySelector(
      ".clozr-message-assistant:last-of-type"
    );
    if (lastMessage) {
      const textDiv = lastMessage.querySelector(".clozr-message-text");
      if (textDiv) {
        textDiv.classList.remove("clozr-message-loading");
        textDiv.textContent = answer;

        // Smooth scroll to show updated response
        setTimeout(() => {
          conversationContainer.scrollTo({
            top: conversationContainer.scrollHeight,
            behavior: "smooth",
          });
        }, 10);
      }
    }
  }

  async function getChatResponse(question, productId) {
    // Call CLOZR Engine chat endpoint with product context
    if (!initialOverview) {
      throw new Error("Initial overview not available");
    }

    const chatUrl = `${CLOZR_ENGINE_URL}/shopify/products/chat`;

    const requestPayload = {
      product_id: productId,
      shop_domain: shop,
      initial_overview: initialOverview,
      question: question,
    };

    try {
      const response = await fetch(chatUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestPayload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Chat API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      return (
        data.response ||
        "I apologize, but I couldn't generate a response. Please try again."
      );
    } catch (error) {
      console.error("CLOZR Chat error:", error);
      console.error("CLOZR Chat request payload:", requestPayload);
      console.error("CLOZR Chat URL:", chatUrl);
      throw error;
    }
  }

  function renderError(err) {
    let errorMessage = "Product insights are temporarily unavailable.";
    if (err.message && err.message.includes("not found")) {
      errorMessage =
        "This product is being processed. Insights will be available soon.";
    }

    wrapper.innerHTML = `
      <div class="clozr-container">
        <div class="clozr-error">
          <span class="clozr-error-text">${escapeHtml(errorMessage)}</span>
        </div>
      </div>
    `;
  }
});

// Inject premium styles
const style = document.createElement("style");
style.textContent = `
  .clozr-container {
    max-width: 100%;
    margin: 2rem 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
    box-sizing: border-box;
  }
  
  #clozr-ai-wrapper {
    display: block;
    box-sizing: border-box;
  }

  /* Unified Overview Block */
  .clozr-overview {
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 8px;
    padding: 0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    height: 240px;
    max-height: 240px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-sizing: border-box;
  }

  /* Sticky Title */
  .clozr-title {
    font-size: 0.875rem;
    font-weight: 500;
    color: #1f2937;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    flex-shrink: 0;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }

  /* Scrollable Conversation Area */
  .clozr-conversation {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1.25rem 1.5rem;
    scroll-behavior: smooth;
  }

  .clozr-conversation::-webkit-scrollbar {
    width: 3px;
  }

  .clozr-conversation::-webkit-scrollbar-track {
    background: transparent;
  }

  .clozr-conversation::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.08);
    border-radius: 3px;
  }

  .clozr-conversation::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.12);
  }

  /* Message Styles */
  .clozr-message {
    margin-bottom: 1.5rem;
    animation: fadeInUp 0.2s ease-out;
  }

  .clozr-message:last-child {
    margin-bottom: 0;
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(1px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .clozr-message-assistant {
    color: #111827;
  }

  .clozr-message-user {
    color: #374151;
  }

  .clozr-message-text {
    font-size: 0.9375rem;
    line-height: 1.65;
    color: inherit;
    font-weight: 400;
    letter-spacing: -0.01em;
  }

  .clozr-message-loading {
    color: #9ca3af;
    font-style: normal;
  }

  .clozr-message-bullets {
    list-style: none;
    padding: 0;
    margin: 0.875rem 0 0 0;
  }

  .clozr-message-bullets li {
    font-size: 0.9375rem;
    line-height: 1.7;
    padding: 0.375rem 0;
    padding-left: 1.375rem;
    position: relative;
    color: inherit;
    font-weight: 400;
    letter-spacing: -0.01em;
  }

  .clozr-message-bullets li::before {
    content: '•';
    position: absolute;
    left: 0.5rem;
    color: #d1d5db;
    font-weight: 400;
    font-size: 1.125rem;
    line-height: 1.4;
  }

  /* Prompt Pills */
  .clozr-prompt-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1.25rem 0 1.5rem 0;
  }

  .clozr-pill {
    padding: 0.4375rem 0.875rem;
    font-size: 0.8125rem;
    color: #6b7280;
    background: transparent;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
    font-weight: 400;
    letter-spacing: -0.01em;
  }

  .clozr-pill:hover {
    background: #f9fafb;
    border-color: rgba(0, 0, 0, 0.1);
    color: #374151;
  }

  .clozr-pill:active {
    transform: scale(0.98);
    background: #f3f4f6;
  }

  /* Q&A Responses Container */
  .clozr-responses {
    margin-top: 0;
  }

  /* Input Field (Fixed at bottom) - Product Query Bar */
  .clozr-input-wrapper {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    background: #ffffff;
    border-top: 1px solid rgba(0, 0, 0, 0.05);
    padding: 1rem 1.5rem;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .clozr-input {
    flex: 1;
    border: 1px solid rgba(0, 0, 0, 0.08);
    outline: none;
    font-size: 0.875rem;
    color: #111827;
    background: #fafafa;
    font-family: inherit;
    padding: 0.625rem 1rem;
    border-radius: 24px;
    transition: all 0.2s ease;
    letter-spacing: -0.01em;
  }

  .clozr-input:focus {
    background: #ffffff;
    border-color: rgba(0, 0, 0, 0.12);
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.02);
  }

  .clozr-input::placeholder {
    color: #9ca3af;
    font-weight: 400;
  }

  .clozr-send {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: none;
    background: #111827;
    color: #ffffff;
    border-radius: 18px;
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
    opacity: 0.9;
  }

  .clozr-send:hover {
    background: #1f2937;
    opacity: 1;
  }

  .clozr-send:active {
    transform: scale(0.96);
  }

  .clozr-send svg {
    width: 16px;
    height: 16px;
  }

  /* Loading & Error States */
  .clozr-loading,
  .clozr-error {
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
  }

  .clozr-loading-text,
  .clozr-error-text {
    font-size: 0.9375rem;
    color: #6b7280;
    font-weight: 400;
    letter-spacing: -0.01em;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .clozr-overview {
      height: 300px;
      max-height: 300px;
    }

    .clozr-title {
      padding: 0.875rem 1.25rem;
    }

    .clozr-conversation {
      padding: 1rem 1.25rem;
    }

    .clozr-message {
      margin-bottom: 1.25rem;
    }

    .clozr-message-text {
      font-size: 0.875rem;
      line-height: 1.6;
    }

    .clozr-message-bullets li {
      font-size: 0.875rem;
      padding: 0.3125rem 0;
      padding-left: 1.25rem;
    }

    .clozr-prompt-pills {
      gap: 0.4375rem;
      margin: 1rem 0 1.25rem 0;
    }

    .clozr-pill {
      font-size: 0.75rem;
      padding: 0.375rem 0.75rem;
    }

    .clozr-input-wrapper {
      padding: 0.875rem 1.25rem;
    }

    .clozr-input {
      font-size: 0.8125rem;
      padding: 0.5625rem 0.875rem;
    }

    .clozr-send {
      width: 32px;
      height: 32px;
    }

    .clozr-send svg {
      width: 14px;
      height: 14px;
    }
  }
`;

document.head.appendChild(style);

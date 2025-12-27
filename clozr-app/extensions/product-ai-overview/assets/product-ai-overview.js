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

  // Fallback prompt suggestions (used if API doesn't provide questions)
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

    // Extract AI-generated suggested questions, fallback to defaults
    const suggestedQuestions =
      data.suggested_questions &&
      Array.isArray(data.suggested_questions) &&
      data.suggested_questions.length > 0
        ? data.suggested_questions
        : defaultPrompts;

    // 3️⃣ Render unified overview block with summary and chat
    renderUnifiedOverview(data, suggestedQuestions);
  } catch (err) {
    console.error("CLOZR AI error:", err);
    renderError(err);
  }

  function renderUnifiedOverview(data, suggestedQuestions = defaultPrompts) {
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
          <div class="clozr-title">Product Overview</div>

          <!-- Scrollable Conversation Area -->
          <div class="clozr-conversation" id="clozr-conversation">
            <!-- Initial Summary as First Message -->
            <div class="clozr-message clozr-message-assistant">
              ${summaryContent}
            </div>

            <!-- Q&A Responses Container -->
            <div class="clozr-responses" id="clozr-responses"></div>
          </div>

          <!-- Prompt Pills (AI-generated or fallback) - Right above input -->
          <div class="clozr-prompt-pills" id="clozr-prompt-pills">
            ${suggestedQuestions
              .slice(0, 4) // Limit to 4 questions max
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

          <!-- Input Field (Fixed at bottom) -->
          <div class="clozr-input-wrapper">
            <div class="clozr-input-container">
              <input 
                type="text" 
                class="clozr-input" 
                id="clozr-input"
                placeholder="Ask me anything about this product..."
                onkeypress="handleClozrKeyPress(event)"
              />
            <button class="clozr-send" onclick="sendClozrMessage()" aria-label="Send">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 19V5M12 5L5 12M12 5L19 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            </div>
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
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, system-ui, sans-serif;
    box-sizing: border-box;
  }
  
  #clozr-ai-wrapper {
    display: block;
    box-sizing: border-box;
  }

  /* Unified Overview Block */
  .clozr-overview {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 0.05);
    border-radius: 8px;
    padding: 0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    height: 300px;
    max-height: 300px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-sizing: border-box;
  }

  /* Sticky Title */
  .clozr-title {
    font-size: 12px;
    font-weight: 600;
    color: #1f2937;
    padding: 18px 20px 8px 20px;
    flex-shrink: 0;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    line-height: 1.2;
  }

  /* Scrollable Conversation Area */
  .clozr-conversation {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 0 20px 18px 20px;
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
    margin-bottom: 1rem;
    animation: fadeInUp 0.2s ease-out;
  }

  .clozr-message:last-child {
    margin-bottom: 0;
  }

  /* First message (summary) - no extra margin since pills moved */
  .clozr-message-assistant:first-of-type {
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
    font-size: 14px;
    line-height: 1.45;
    color: inherit;
    font-weight: 400;
    letter-spacing: -0.01em;
    max-width: 48ch;
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

  /* Prompt Pills - Right above input field */
  .clozr-prompt-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding: 0 20px 8px 20px;
    flex-shrink: 0;
  }

  .clozr-pill {
    padding: 6px 12px;
    font-size: 12px;
    color: #6b7280;
    background: transparent;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
    font-weight: 500;
    line-height: 1.2;
    letter-spacing: -0.01em;
    opacity: 0.85;
    text-align: left;
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
    background: #ffffff;
    padding: 0 20px 18px 20px;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .clozr-input-container {
    display: flex;
    align-items: center;
    position: relative;
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 24px;
    min-height: 40px;
  }

  .clozr-input-container:focus-within {
    outline: none;
    border-color: rgba(0, 0, 0, 0.1);
  }

  .clozr-input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 12px;
    line-height: 1.3;
    color: #111827;
    background: transparent;
    font-family: inherit;
    font-weight: 400;
    padding: 0.875rem 1.125rem 0.875rem 1.375rem;
    border-radius: 24px;
    letter-spacing: -0.01em;
  }

  .clozr-input:focus {
    outline: none;
    box-shadow: none;
  }

  .clozr-input::placeholder {
    color: #9ca3af;
    font-weight: 400;
    opacity: 0.6;
  }

  .clozr-send {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    margin-right: 0.5rem;
    border: none;
    background: #111827;
    color: #ffffff;
    border-radius: 50%;
    cursor: pointer;
    flex-shrink: 0;
    opacity: 0.9;
    padding: 0;
    line-height: 0;
  }

  .clozr-send:hover {
    background: #1f2937;
    opacity: 1;
  }

  .clozr-send:active {
    transform: scale(0.96);
  }

  .clozr-send svg {
    width: 14px;
    height: 14px;
    display: block;
    margin: 0;
    padding: 0;
    flex-shrink: 0;
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
      padding: 0.875rem 1.25rem 0.5rem 1.25rem;
    }

    .clozr-conversation {
      padding: 0 1.25rem 0.875rem 1.25rem;
    }

    .clozr-message {
      margin-bottom: 0.875rem;
    }

    .clozr-message-assistant:first-of-type {
      margin-bottom: 1rem;
    }

    .clozr-message-text {
      font-size: 1rem;
      line-height: 1.6;
    }

    .clozr-message-bullets li {
      font-size: 0.875rem;
      padding: 0.3125rem 0;
      padding-left: 1.25rem;
    }

    .clozr-prompt-pills {
      gap: 0.4375rem;
      padding: 0 20px 8px 20px;
    }

    .clozr-pill {
      font-size: 12px;
      font-weight: 500;
      line-height: 1.2;
      padding: 6px 12px;
      opacity: 0.85;
    }

    .clozr-input-wrapper {
      padding: 0 20px 18px 20px;
    }

    .clozr-input {
      font-size: 12px;
      line-height: 1.3;
      padding: 0.875rem 1rem 0.875rem 1.25rem;
    }

    .clozr-send {
      width: 26px;
      height: 26px;
      margin-right: 0.4375rem;
    }

    .clozr-send svg {
      width: 12px;
      height: 12px;
    }

    .clozr-input::placeholder {
      opacity: 0.6;
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

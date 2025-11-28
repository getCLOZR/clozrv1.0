/**
 * CLOZR Product Overview JavaScript
 * Fetches and displays AI-generated product overviews
 */

(function() {
  'use strict';

  // Configuration
  const CLOZR_ENGINE_API = 'https://your-clozr-engine-url.com/api'; // TODO: Update with actual engine URL
  const PRODUCT_ID_ATTRIBUTE = 'data-product-id';
  const PRODUCT_HANDLE_ATTRIBUTE = 'data-product-handle';

  /**
   * Fetch product overview from CLOZR Engine
   */
  async function fetchProductOverview(productId, productHandle) {
    try {
      const response = await fetch(`${CLOZR_ENGINE_API}/products/${productId}/overview`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch overview: ${response.statusText}`);
      }

      const data = await response.json();
      return data.overview || data.html || null;
    } catch (error) {
      console.error('CLOZR: Error fetching product overview:', error);
      return null;
    }
  }

  /**
   * Render overview content into the container
   */
  function renderOverview(container, overviewHtml) {
    const loadingEl = container.querySelector('.clozr-overview-loading');
    const contentEl = container.querySelector('.clozr-overview-content');

    if (loadingEl) {
      loadingEl.style.display = 'none';
    }

    if (contentEl && overviewHtml) {
      contentEl.innerHTML = overviewHtml;
      contentEl.style.display = 'block';
    } else if (contentEl) {
      contentEl.style.display = 'none';
    }
  }

  /**
   * Initialize overview for a product container
   */
  async function initOverview(container) {
    const productId = container.getAttribute(PRODUCT_ID_ATTRIBUTE);
    const productHandle = container.getAttribute(PRODUCT_HANDLE_ATTRIBUTE);

    if (!productId) {
      console.warn('CLOZR: Product ID not found');
      return;
    }

    // Show loading state
    const loadingEl = container.querySelector('.clozr-overview-loading');
    if (loadingEl) {
      loadingEl.style.display = 'block';
    }

    // Fetch and render overview
    const overviewHtml = await fetchProductOverview(productId, productHandle);
    renderOverview(container, overviewHtml);
  }

  /**
   * Initialize all overview containers on the page
   */
  function init() {
    const containers = document.querySelectorAll('.clozr-overview-container');
    
    if (containers.length === 0) {
      return;
    }

    containers.forEach(container => {
      initOverview(container);
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Re-initialize on dynamic content changes (for SPA themes)
  if (typeof window !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
      const hasNewContainers = Array.from(mutations).some(mutation => {
        return Array.from(mutation.addedNodes).some(node => {
          return node.nodeType === 1 && (
            node.classList.contains('clozr-overview-container') ||
            node.querySelector('.clozr-overview-container')
          );
        });
      });

      if (hasNewContainers) {
        init();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
})();


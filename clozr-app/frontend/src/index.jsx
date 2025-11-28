import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Initialize Shopify App Bridge
// Note: App Bridge will be loaded by Shopify's embedded app context
// In production, configure App Bridge here if needed

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);


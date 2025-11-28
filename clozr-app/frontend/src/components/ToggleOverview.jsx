import React from "react";
import { Toggle, Text } from "@shopify/polaris";

/**
 * ToggleOverview Component
 * Reusable component for enabling/disabling product overview
 */
function ToggleOverview({ enabled, onToggle }) {
  return (
    <div>
      <Toggle
        label="Enable Product Overview"
        checked={enabled}
        onChange={onToggle}
        helpText="Show AI-generated overview on product pages"
      />
      {enabled && (
        <div style={{ marginTop: "1rem" }}>
          <Text variant="bodyMd" color="subdued">
            Product overviews will be displayed on all product pages.
          </Text>
        </div>
      )}
    </div>
  );
}

export default ToggleOverview;


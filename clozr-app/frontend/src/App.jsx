import React, { useState } from "react";
import {
  AppProvider,
  Page,
  Card,
  Toggle,
  Text,
  Layout,
  Banner,
} from "@shopify/polaris";
import "@shopify/polaris/build/esm/styles.css";

/**
 * Main App Component
 * Embedded Shopify app using Polaris and App Bridge
 */
function App() {
  const [overviewEnabled, setOverviewEnabled] = useState(false);

  const handleToggleChange = (value) => {
    setOverviewEnabled(value);
    // TODO: Save setting to backend
    console.log("Product Overview enabled:", value);
  };

  return (
    <AppProvider i18n={{}}>
      <Page title="CLOZR Settings">
        <Layout>
          <Layout.Section>
            <Card sectioned>
              <div style={{ marginBottom: "1rem" }}>
                <Text variant="headingMd" as="h2">
                  Product Page AI Overview
                </Text>
                <Text variant="bodyMd" color="subdued" as="p">
                  Enable AI-generated product overviews on your product pages.
                </Text>
              </div>
              <Toggle
                label="Enable Product Overview"
                checked={overviewEnabled}
                onChange={handleToggleChange}
              />
            </Card>
          </Layout.Section>
          {overviewEnabled && (
            <Layout.Section>
              <Banner status="info">
                <Text as="p">
                  Product Overview is now enabled. The AI overview will appear
                  on your product pages.
                </Text>
              </Banner>
            </Layout.Section>
          )}
        </Layout>
      </Page>
    </AppProvider>
  );
}

export default App;


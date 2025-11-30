import { useState, useEffect } from "react";
import { AppProvider, Page, Layout, Card, Text } from "@shopify/polaris";
import {
  Provider as AppBridgeProvider,
  useAppBridge,
} from "@shopify/app-bridge-react";
import { getSessionToken } from "@shopify/app-bridge-utils";

function ProductCount() {
  const app = useAppBridge();
  const [count, setCount] = useState(null);

  useEffect(() => {
    const fetchCount = async () => {
      const shop = new URLSearchParams(window.location.search).get("shop");
      const token = await getSessionToken(app);

      const res = await fetch(`/api/products?shop=${shop}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      setCount(data.count);
    };

    fetchCount();
  }, [app]);

  return (
    <Card>
      <Text variant="headingMd">Product Count</Text>
      <Text>{count !== null ? count : "Loading..."}</Text>
    </Card>
  );
}

export default function App() {
  const shop = new URLSearchParams(window.location.search).get("shop");

  // Get API key from env or use placeholder (will work in embedded context)
  const apiKey = import.meta.env.VITE_SHOPIFY_API_KEY || "placeholder";
  const host = new URL(location.href).searchParams.get("host");

  // Content to render
  const appContent = (
    <AppProvider>
      <Page title="CLOZR Dashboard">
        <Layout>
          <Layout.Section>
            <Card>
              <Text variant="headingLg">Welcome to CLOZR 🎉</Text>
              <Text>Shop: {shop || "Not provided"}</Text>
            </Card>
          </Layout.Section>

          <Layout.Section>
            {host ? (
              <ProductCount />
            ) : (
              <Card>
                <Text>Waiting for Shopify context...</Text>
              </Card>
            )}
          </Layout.Section>
        </Layout>
      </Page>
    </AppProvider>
  );

  // Only wrap with AppBridgeProvider if we have host (embedded context)
  if (host && apiKey !== "placeholder") {
    return (
      <AppBridgeProvider
        config={{
          apiKey: apiKey,
          host: host,
          forceRedirect: true,
        }}
      >
        {appContent}
      </AppBridgeProvider>
    );
  }

  // Fallback: render without App Bridge (for testing or missing config)
  return appContent;
}

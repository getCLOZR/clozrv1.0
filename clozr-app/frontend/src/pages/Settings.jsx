import { useEffect, useState } from "react";
import { Card, Button, Checkbox, Text, Banner } from "@shopify/polaris";
import { useAppBridge } from "@shopify/app-bridge-react";
import { getSessionToken } from "@shopify/app-bridge-utils";

export default function SettingsPage() {
  const app = useAppBridge();
  const shop = new URLSearchParams(window.location.search).get("shop");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Settings fields
  const [overviewEnabled, setOverviewEnabled] = useState(false);

  // Fetch settings on load
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setError(null);
        const token = await getSessionToken(app);

        const res = await fetch(`/api/settings?shop=${shop}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (res.ok) {
          const data = await res.json();
          setOverviewEnabled(data.overview_enabled ?? false);
        } else {
          setError(`Failed to load settings: ${res.statusText}`);
        }
      } catch (err) {
        console.error("Error fetching settings:", err);
        setError(`Error loading settings: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    if (app && shop) {
      fetchSettings();
    } else {
      setError("Missing app context or shop parameter");
      setLoading(false);
    }
  }, [app, shop]);

  // Save settings
  const saveSettings = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);

      const token = await getSessionToken(app);

      const res = await fetch(`/api/settings?shop=${shop}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          overview_enabled: overviewEnabled,
        }),
      });

      if (!res.ok) {
        setError(`Failed to save settings: ${res.statusText}`);
      } else {
        setSuccess(true);
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (err) {
      console.error("Error saving settings:", err);
      setError(`Error saving settings: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {error && (
        <Banner status="critical" onDismiss={() => setError(null)}>
          <p>{error}</p>
        </Banner>
      )}
      {success && (
        <Banner status="success" onDismiss={() => setSuccess(false)}>
          <p>Settings saved successfully!</p>
        </Banner>
      )}
      <Card>
        <Text variant="headingLg">Product Page AI Overview</Text>

        {loading ? (
          <Text>Loading settings...</Text>
        ) : (
          <>
            <Checkbox
              label="Enable AI Overview on product pages"
              checked={overviewEnabled}
              onChange={setOverviewEnabled}
            />

            <div style={{ marginTop: "1rem" }} />

            <Button primary onClick={saveSettings} loading={saving}>
              Save Settings
            </Button>
          </>
        )}
      </Card>
    </>
  );
}

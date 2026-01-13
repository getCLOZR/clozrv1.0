import { Component } from "react";
import { Card, Text, Button } from "@shopify/polaris";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card>
          <Text variant="headingMd" as="h2">
            Something went wrong
          </Text>
          <Text as="p">
            {this.state.error?.message || "An unexpected error occurred"}
          </Text>
          <div style={{ marginTop: "1rem" }}>
            <Button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
            >
              Reload Page
            </Button>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;









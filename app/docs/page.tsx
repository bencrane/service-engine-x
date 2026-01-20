"use client";

import { useEffect, useRef } from "react";
import Script from "next/script";

declare global {
  interface Window {
    SwaggerUIBundle: {
      (config: object): void;
      presets: {
        apis: unknown;
      };
    };
  }
}

export default function DocsPage() {
  const initialized = useRef(false);

  const initSwagger = () => {
    if (initialized.current) return;
    if (typeof window !== "undefined" && window.SwaggerUIBundle) {
      initialized.current = true;
      window.SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        presets: [window.SwaggerUIBundle.presets.apis],
        layout: "BaseLayout",
        deepLinking: true,
      });
    }
  };

  useEffect(() => {
    // Check if script already loaded (e.g., from cache)
    if (typeof window.SwaggerUIBundle !== "undefined") {
      initSwagger();
    }
  }, []);

  return (
    <>
      <Script
        src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"
        strategy="afterInteractive"
        onLoad={initSwagger}
      />
      <link
        rel="stylesheet"
        href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
      />
      <div
        id="swagger-ui"
        style={{ minHeight: "100vh", backgroundColor: "#fff" }}
      />
    </>
  );
}

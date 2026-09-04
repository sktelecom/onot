import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { initTheme } from "./lib/theme";
import "./index.css";

// Before the first render, and only for a user who overrode the OS setting. The default needs
// nothing: the stylesheet already follows the OS. An inline script in index.html would run
// marginally earlier but the app serves a "script-src 'self'" CSP, which blocks inline scripts.
initTheme();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

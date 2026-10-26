import React from "react";
import ReactDOM from "react-dom/client";
import { MantineProvider } from "@mantine/core";

// Mantine stylesheets - order matters: core first, then add-ons.
import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/charts/styles.css";
import "./styles.css";

import { theme } from "./theme.js";
import App from "./App.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <App />
    </MantineProvider>
  </React.StrictMode>
);

import { createTheme } from "@mantine/core";

// App-wide Mantine theme. Teal primary reads as "air / clean" and pairs well
// with the dark dashboard surfaces.
export const theme = createTheme({
  primaryColor: "teal",
  defaultRadius: "md",
  fontFamily:
    "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
  headings: {
    fontWeight: "650",
    sizes: { h1: { fontSize: "1.6rem" } },
  },
});

// Shared app metadata - edit REPO_URL to your repository.
export const APP = {
  name: "Saans",
  tagline: "India air quality, tracked - with optional case overlays from official data",
  repoUrl: "https://github.com/syedtasavour/Saans",
  author: { name: "Syed Tasavour", url: "https://syedtasavour.com" },
};

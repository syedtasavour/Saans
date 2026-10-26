// Single place that talks to the backend. Components call these helpers and
// never build URLs themselves.

const BASE = import.meta.env.VITE_API_BASE ?? ""; // "" -> Vite proxy in dev

async function getJSON(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}${detail ? ` - ${detail}` : ""}`);
  }
  return res.json();
}

export const api = {
  states: () => getJSON("/api/states"),
  healthNote: () => getJSON("/api/health-note"),
  meta: () => getJSON("/api/meta"),
  overview: ({ state, granularity, from, to }) => {
    const qs = new URLSearchParams({ state, granularity });
    if (from) qs.set("from", from);
    if (to) qs.set("to", to);
    return getJSON(`/api/overview?${qs.toString()}`);
  },
  live: (state) => getJSON(`/api/live?state=${encodeURIComponent(state)}`),
};

import { Badge, Group, Paper, SimpleGrid, Text } from "@mantine/core";

const POLLUTANT_LABELS = {
  pm25: "PM2.5",
  pm10: "PM10",
  no2: "NO₂",
  so2: "SO₂",
  o3: "O₃",
  co: "CO",
};

// CPCB-style PM2.5 bands.
function pm25Band(v) {
  if (v == null) return null;
  if (v <= 30) return { label: "Good", color: "green" };
  if (v <= 60) return { label: "Satisfactory", color: "teal" };
  if (v <= 90) return { label: "Moderate", color: "yellow" };
  if (v <= 120) return { label: "Poor", color: "orange" };
  return { label: "Very poor", color: "red" };
}

function Kpi({ label, value, unit, badge }) {
  return (
    <Paper withBorder radius="md" p="md">
      <Text size="xs" c="dimmed">{label}</Text>
      <Group gap="xs" align="baseline" mt={4}>
        <Text fw={650} fz={26} lh={1}>{value}</Text>
        {unit && <Text size="xs" c="dimmed">{unit}</Text>}
      </Group>
      {badge && <Badge color={badge.color} variant="light" mt={6}>{badge.label}</Badge>}
    </Paper>
  );
}

const fmt = (n) => (n == null ? "-" : n.toLocaleString("en-IN"));

export default function KpiCards({ latest, pollutant = "pm25", hasCases }) {
  if (!latest) return null;
  const label = POLLUTANT_LABELS[pollutant] ?? pollutant;
  const band = pollutant === "pm25" ? pm25Band(latest.pm25) : null;

  // With real case data, lead with pollutant + case metrics; otherwise show a
  // row of air-quality metrics only.
  const cards = hasCases
    ? [
        { label: `${label} · ${latest.period}`, value: latest[pollutant] ?? "-", unit: "µg/m³", badge: band },
        { label: "ARI cases", value: fmt(latest.ari_cases) },
        { label: "ARI deaths", value: fmt(latest.ari_deaths) },
        { label: "PM10", value: latest.pm10 ?? "-", unit: "µg/m³" },
      ]
    : [
        { label: `${label} · ${latest.period}`, value: latest[pollutant] ?? "-", unit: "µg/m³", badge: band },
        { label: "PM10", value: latest.pm10 ?? "-", unit: "µg/m³" },
        { label: "NO₂", value: latest.no2 ?? "-", unit: "µg/m³" },
        { label: "O₃", value: latest.o3 ?? "-", unit: "µg/m³" },
      ];

  return (
    <SimpleGrid cols={{ base: 2, sm: 4 }} spacing="sm">
      {cards.map((c) => <Kpi key={c.label} {...c} />)}
    </SimpleGrid>
  );
}

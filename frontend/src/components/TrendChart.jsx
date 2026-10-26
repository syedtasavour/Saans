import { CompositeChart } from "@mantine/charts";
import { Card, Group, Text, Title } from "@mantine/core";

const POLLUTANT_LABELS = {
  pm25: "PM2.5",
  pm10: "PM10",
  no2: "NO₂",
  so2: "SO₂",
  o3: "O₃",
  co: "CO",
};

// Selected pollutant as a line (left axis). If real case data is present, add
// case bars on a right axis; otherwise it's a clean air-quality trend.
export default function TrendChart({ points, pollutant = "pm25", hasCases }) {
  const label = POLLUTANT_LABELS[pollutant] ?? pollutant;

  const series = [{ name: pollutant, label, color: "teal.5", type: "line" }];
  if (hasCases) {
    series.unshift(
      { name: "ari_cases", label: "ARI cases", color: "orange.5", type: "bar", yAxisId: "right" }
    );
  }

  return (
    <Card withBorder radius="md" p="md" h="100%">
      <Group justify="space-between" mb="xs">
        <Title order={4}>{hasCases ? `${label} vs respiratory cases` : `${label} trend`}</Title>
        <Text size="xs" c="dimmed">
          {hasCases ? "line = µg/m³ · bars = reported cases" : "µg/m³ (period average)"}
        </Text>
      </Group>
      <CompositeChart
        h={360}
        data={points}
        dataKey="period"
        series={series}
        curveType="monotone"
        withRightYAxis={hasCases}
        yAxisLabel={label}
        rightYAxisLabel={hasCases ? "cases" : undefined}
        withLegend
        legendProps={{ verticalAlign: "bottom" }}
        tooltipAnimationDuration={150}
        strokeWidth={2.5}
        gridAxis="xy"
      />
    </Card>
  );
}

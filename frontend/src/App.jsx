import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Anchor,
  Badge,
  Button,
  Container,
  Grid,
  Group,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { IconBrandGithub, IconStar } from "@tabler/icons-react";
import dayjs from "dayjs";

import { api } from "./api.js";
import { APP } from "./theme.js";
import { useAsync } from "./hooks/useAsync.js";
import Controls from "./components/Controls.jsx";
import KpiCards from "./components/KpiCards.jsx";
import TrendChart from "./components/TrendChart.jsx";
import LiveStation from "./components/LiveStation.jsx";
import Notice from "./components/Notice.jsx";

const DEFAULT_POLLUTANTS = ["pm25", "pm10", "no2", "so2", "o3", "co"];
const toISO = (d) => (d ? dayjs(d).format("YYYY-MM-DD") : "");

export default function App() {
  const [states, setStates] = useState([]);
  const [meta, setMeta] = useState({ date_min: "", date_max: "", pollutants: DEFAULT_POLLUTANTS });
  const [state, setState] = useState("Jammu and Kashmir");
  const [granularity, setGranularity] = useState("year");
  const [pollutant, setPollutant] = useState("pm25");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [quickRange, setQuickRange] = useState("all");

  useEffect(() => {
    api.states().then((d) => setStates(d.states)).catch(() => setStates(["Jammu and Kashmir"]));
    api.meta().then((m) => {
      setMeta(m);
      setDateFrom(m.date_min || "");
      setDateTo(m.date_max || "");
    }).catch(() => {});
  }, []);

  const { data, loading, error } = useAsync(
    () => api.overview({ state, granularity, from: dateFrom, to: dateTo }),
    [state, granularity, dateFrom, dateTo]
  );

  const points = data?.points ?? [];
  const latest = useMemo(() => (points.length ? points[points.length - 1] : null), [points]);
  const hasCases = useMemo(
    () => points.some((p) => p.ari_cases != null || p.severe_cases != null),
    [points]
  );

  function applyQuickRange(value) {
    setQuickRange(value);
    const max = meta.date_max;
    const min = meta.date_min;
    if (!max) return;
    if (value === "all") {
      setDateFrom(min || "");
    } else {
      const days = { "30d": 30, "90d": 90, "1y": 365 }[value];
      const candidate = dayjs(max).subtract(days, "day").format("YYYY-MM-DD");
      setDateFrom(min && candidate < min ? min : candidate);
    }
    setDateTo(max);
  }

  // Manual date edits clear the active quick-range selection.
  const onDateFrom = (d) => { setQuickRange(""); setDateFrom(toISO(d)); };
  const onDateTo = (d) => { setQuickRange(""); setDateTo(toISO(d)); };

  return (
    <Container size="lg" py="xl">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <div>
            <Group gap="sm" align="center">
              <Title order={1}>{APP.name}</Title>
              <Badge variant="light" color="teal">India</Badge>
            </Group>
            <Text c="dimmed" size="sm">{APP.tagline}</Text>
          </div>
          <Group gap="xs">
            {points.length > 0 && (
              <Badge variant="default" size="lg">
                {points.length} period{points.length === 1 ? "" : "s"}
              </Badge>
            )}
            <Button
              component="a"
              href={APP.repoUrl}
              target="_blank"
              rel="noreferrer"
              variant="light"
              leftSection={<IconStar size={16} />}
            >
              Star
            </Button>
          </Group>
        </Group>

        <Notice />

        <Controls
          states={states}
          state={state}
          granularity={granularity}
          pollutant={pollutant}
          pollutants={meta.pollutants || DEFAULT_POLLUTANTS}
          dateFrom={dateFrom}
          dateTo={dateTo}
          bounds={meta}
          quickRange={quickRange}
          onState={setState}
          onGranularity={setGranularity}
          onPollutant={setPollutant}
          onDateFrom={onDateFrom}
          onDateTo={onDateTo}
          onQuickRange={applyQuickRange}
        />

        {error && <Alert color="red" variant="light" title="Failed to load">{error}</Alert>}

        <KpiCards latest={latest} pollutant={pollutant} hasCases={hasCases} />

        <Grid gutter="md">
          <Grid.Col span={{ base: 12, md: 8 }}>
            {loading ? (
              <Alert variant="light" color="gray">Loading {granularity} data for {state}…</Alert>
            ) : (
              <TrendChart points={points} pollutant={pollutant} hasCases={hasCases} />
            )}
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <LiveStation state={state} />
          </Grid.Col>
        </Grid>

        <Group justify="space-between" mt="md" pt="md" style={{ borderTop: "1px solid var(--mantine-color-dark-4)" }}>
          <Text size="xs" c="dimmed">
            Air quality: Open-Meteo (CAMS) · Live stations: OpenAQ / CPCB · Cases: official data (NHP / IDSP), optional.
          </Text>
          <Group gap="xs">
            <Text size="xs" c="dimmed">
              Built by <Anchor href={APP.author.url} target="_blank" rel="noreferrer">{APP.author.name}</Anchor>
            </Text>
            <Anchor href={APP.repoUrl} target="_blank" rel="noreferrer" size="xs">
              <Group gap={4}><IconBrandGithub size={14} /> Star the repo</Group>
            </Anchor>
          </Group>
        </Group>
      </Stack>
    </Container>
  );
}

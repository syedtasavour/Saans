import { Badge, Card, Group, Loader, Stack, Text, Title } from "@mantine/core";
import { IconBroadcast } from "@tabler/icons-react";
import { api } from "../api.js";
import { useAsync } from "../hooks/useAsync.js";

// Nearest real CPCB / state-board monitoring station (via OpenAQ).
export default function LiveStation({ state }) {
  const { data, loading, error } = useAsync(() => api.live(state), [state]);
  const live = data?.live;
  const asOf = live?.readings?.[0]?.datetime;

  return (
    <Card withBorder radius="md" p="md" h="100%">
      <Group gap="xs" mb="xs">
        <IconBroadcast size={18} color="var(--mantine-color-teal-5)" />
        <Title order={5}>Live govt station</Title>
      </Group>

      {loading && <Group gap="xs"><Loader size="xs" /><Text size="sm" c="dimmed">Loading…</Text></Group>}
      {error && <Text size="sm" c="red">Station unavailable</Text>}

      {live && (
        <>
          <Text fw={600} size="sm">{live.station}</Text>
          <Text size="xs" c="dimmed" mb="sm">
            {live.provider} · nearest to {data.city}
          </Text>
          <Stack gap={8}>
            {(live.readings || []).map((r) => (
              <Group key={r.parameter} justify="space-between">
                <Text size="sm" c="dimmed">{r.parameter}</Text>
                <Text size="sm" fw={600}>
                  {r.value} <Text span size="xs" c="dimmed">{r.unit}</Text>
                </Text>
              </Group>
            ))}
          </Stack>
          {asOf && (
            <Badge variant="light" color="gray" mt="sm">
              as of {new Date(asOf).toLocaleString("en-IN")}
            </Badge>
          )}
        </>
      )}
      {data && !live && !loading && <Text size="sm" c="dimmed">No station found nearby.</Text>}
    </Card>
  );
}

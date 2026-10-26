import { Group, Paper, SegmentedControl, Select } from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";

const GRANULARITIES = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
  { value: "year", label: "Year" },
];

const QUICK_RANGES = [
  { value: "30d", label: "30d" },
  { value: "90d", label: "90d" },
  { value: "1y", label: "1y" },
  { value: "all", label: "All" },
];

const POLLUTANT_LABELS = {
  pm25: "PM2.5",
  pm10: "PM10",
  no2: "NO₂",
  so2: "SO₂",
  o3: "O₃",
  co: "CO",
};

const toDate = (iso) => (iso ? new Date(iso) : null);

export default function Controls({
  states,
  state,
  granularity,
  pollutant,
  pollutants,
  dateFrom,
  dateTo,
  bounds,
  quickRange,
  onState,
  onGranularity,
  onPollutant,
  onDateFrom,
  onDateTo,
  onQuickRange,
}) {
  const minDate = toDate(bounds?.date_min);
  const maxDate = toDate(bounds?.date_max);

  return (
    <Paper withBorder p="md" radius="md">
      <Group align="flex-end" gap="lg" wrap="wrap">
        <Select
          label="State"
          data={states}
          value={state}
          onChange={(v) => v && onState(v)}
          searchable
          allowDeselect={false}
          w={200}
        />

        <Select
          label="Pollutant"
          data={pollutants.map((p) => ({ value: p, label: POLLUTANT_LABELS[p] ?? p }))}
          value={pollutant}
          onChange={(v) => v && onPollutant(v)}
          allowDeselect={false}
          w={130}
        />

        <div>
          <TextLabel>Granularity</TextLabel>
          <SegmentedControl
            value={granularity}
            onChange={onGranularity}
            data={GRANULARITIES}
          />
        </div>

        <DatePickerInput
          label="From"
          value={toDate(dateFrom)}
          onChange={onDateFrom}
          minDate={minDate}
          maxDate={toDate(dateTo) || maxDate}
          valueFormat="DD MMM YYYY"
          w={150}
          clearable={false}
        />

        <DatePickerInput
          label="To"
          value={toDate(dateTo)}
          onChange={onDateTo}
          minDate={toDate(dateFrom) || minDate}
          maxDate={maxDate}
          valueFormat="DD MMM YYYY"
          w={150}
          clearable={false}
        />

        <div>
          <TextLabel>Quick range</TextLabel>
          <SegmentedControl
            value={quickRange}
            onChange={onQuickRange}
            data={QUICK_RANGES}
          />
        </div>
      </Group>
    </Paper>
  );
}

// Tiny label that matches Mantine input label styling.
function TextLabel({ children }) {
  return (
    <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 4 }}>{children}</div>
  );
}

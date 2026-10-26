import { Alert } from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";
import { api } from "../api.js";
import { useAsync } from "../hooks/useAsync.js";

// Honest, always-visible statement of what's real vs. optional.
export default function Notice() {
  const { data } = useAsync(() => api.healthNote(), []);
  if (!data?.note) return null;
  return (
    <Alert
      variant="light"
      color="teal"
      radius="md"
      icon={<IconInfoCircle size={18} />}
      title="About the data"
    >
      {data.note}
    </Alert>
  );
}

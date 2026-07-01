type ProductMetricProps = {
  label: string;
  value?: number | string;
  caption?: string;
};

export function ProductMetric({ label, value, caption }: ProductMetricProps) {
  return (
    <div className="metric-chip">
      <span>{label}</span>
      <b>{value ?? "—"}</b>
      {caption ? <small>{caption}</small> : null}
    </div>
  );
}

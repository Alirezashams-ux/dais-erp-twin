export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";

export type Summary = {
  projects?: number;
  datasets?: number;
  model_assets?: number;
  experiments?: number;
  agent_proposals?: number;
};

export type SeverityCounts = {
  critical?: number;
  high?: number;
  medium?: number;
  low?: number;
};

export type DqSummary = {
  issue_types?: number;
  total_issue_instances?: number;
  severity_counts?: SeverityCounts;
};

export type Issue = {
  issue_id?: string;
  severity?: string;
  title?: string;
  count?: number;
  recommended_action?: string;
};

export type Proposal = {
  proposal_id?: string;
  proposal_type?: string;
  title?: string;
  confidence?: number | string;
};

export type Conflict = {
  equipment_id?: string;
  equipment_name?: string;
  reservation_a?: string;
  reservation_b?: string;
  a_start?: string;
};

export type LineageRow = {
  dataset_code?: string;
  model_code?: string;
  experiment_code?: string;
  experiment_status?: string;
  publication_title?: string;
  reproducibility_package_status?: string;
};

export type Project = {
  project_id?: string;
  project_code?: string;
  title?: string;
  theme?: string;
};

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }

  return res.json();
}

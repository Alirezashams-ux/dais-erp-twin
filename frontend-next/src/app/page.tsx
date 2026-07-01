"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BadgeCheck,
  Database,
  FileCheck2,
  Fingerprint,
  GitBranch,
  LockKeyhole,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
  UserCheck,
} from "lucide-react";

import {
  getJson,
  type Conflict,
  type DqSummary,
  type Issue,
  type LineageRow,
  type Project,
  type Proposal,
  type Summary,
} from "../lib/api";

import { ProductMetric } from "../components/ProductMetric";

type DecisionPassport = {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  aiProposal: string;
  evidence: string;
  humanGate: string;
  trustState: string;
};

function shortText(value: unknown, max = 86) {
  if (value === null || value === undefined || value === "") return "—";
  const text = String(value);
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

function confidence(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";
  const n = Number(value);
  if (!Number.isFinite(n)) return String(value);
  if (n <= 1) return `${Math.round(n * 100)}%`;
  return `${Math.round(n)}%`;
}

function severityClass(severity?: string) {
  const s = String(severity || "info").toLowerCase();
  if (s === "critical" || s === "high") return "danger";
  if (s === "medium") return "warning";
  if (s === "low") return "success";
  return "info";
}

function rankSeverity(severity?: string) {
  const s = String(severity || "low").toLowerCase();
  if (s === "critical") return 4;
  if (s === "high") return 3;
  if (s === "medium") return 2;
  return 1;
}

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [lastSync, setLastSync] = useState<string>("Not synced");
  const [error, setError] = useState<string>("");

  const [summary, setSummary] = useState<Summary>({});
  const [dq, setDq] = useState<DqSummary>({});
  const [issues, setIssues] = useState<Issue[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [project, setProject] = useState<Project>({});
  const [lineage, setLineage] = useState<LineageRow[]>([]);
  const [projectId, setProjectId] = useState("PJ-0003");
  const [selectedIssueIndex, setSelectedIssueIndex] = useState(0);

  const sortedIssues = useMemo(() => {
    return [...issues].sort((a, b) => {
      const sev = rankSeverity(b.severity) - rankSeverity(a.severity);
      if (sev !== 0) return sev;
      return Number(b.count || 0) - Number(a.count || 0);
    });
  }, [issues]);

  const selectedIssue = sortedIssues[selectedIssueIndex] || sortedIssues[0];
  const topProposal = proposals[0];
  const topConflict = conflicts[0];

  const trustScore = useMemo(() => {
    const s = dq.severity_counts || {};
    const score =
      100 -
      Number(s.critical || 0) * 18 -
      Number(s.high || 0) * 7 -
      Number(s.medium || 0) * 2 -
      Number(s.low || 0);
    return Math.max(0, Math.min(100, Math.round(score)));
  }, [dq]);

  const passport: DecisionPassport = useMemo(() => {
    if (!isConnected) {
      return {
        id: "BACKEND-OFFLINE",
        title: "The Trust Passport is waiting for the ERP Twin backend.",
        severity: "high",
        aiProposal: "Start FastAPI and PostgreSQL before showing live decision intelligence.",
        evidence: "Frontend could not fetch the backend API.",
        humanGate: "Developer/operator must start the backend service.",
        trustState: error || "Not connected",
      };
    }

    if (selectedIssue) {
      return {
        id: selectedIssue.issue_id || "DQ-RISK",
        title: selectedIssue.title || "Data-quality risk detected",
        severity: String(selectedIssue.severity || "info").toLowerCase() as DecisionPassport["severity"],
        aiProposal:
          selectedIssue.recommended_action ||
          "Route this risk to a human reviewer before automation.",
        evidence: `Detected ${selectedIssue.count ?? "multiple"} linked ERP evidence instance(s).`,
        humanGate:
          "Professor/admin reviews the evidence before any ERP state change is applied.",
        trustState:
          String(selectedIssue.severity || "risk").toUpperCase() +
          " risk · automation should be gated.",
      };
    }

    return {
      id: topProposal?.proposal_id || "AGENT-GATE",
      title: topProposal?.title || "AI proposals require evidence before action.",
      severity: "info",
      aiProposal: topProposal
        ? `${topProposal.proposal_type || "Agent proposal"} · confidence ${confidence(topProposal.confidence)}`
        : "No high-risk proposal selected.",
      evidence: "Agent proposal queue + Data Quality Firewall + project lineage.",
      humanGate: "Human approval remains required for high-risk ERP changes.",
      trustState: "Evidence-governed agentic ERP",
    };
  }, [isConnected, error, selectedIssue, topProposal]);

  async function loadLineage(targetProjectId = projectId) {
    const data = await getJson<{ project?: Project; lineage?: LineageRow[] }>(
      `/lineage/project/${encodeURIComponent(targetProjectId)}`
    );
    setProject(data.project || {});
    setLineage(data.lineage || []);
  }

  async function refreshAll() {
    setIsLoading(true);
    setError("");

    try {
      await getJson("/health");

      const [summaryData, dqData, reportData, proposalData, conflictData] =
        await Promise.all([
          getJson<{ summary?: Summary }>("/summary"),
          getJson<DqSummary>("/data-quality/summary"),
          getJson<{ issues?: Issue[] }>("/data-quality/report"),
          getJson<Proposal[]>("/agent-proposals/high-risk"),
          getJson<Conflict[]>("/equipment/conflicts"),
        ]);

      setSummary(summaryData.summary || {});
      setDq(dqData || {});
      setIssues(reportData.issues || []);
      setProposals(proposalData || []);
      setConflicts(conflictData || []);
      await loadLineage(projectId);

      setIsConnected(true);
      setLastSync(new Date().toLocaleTimeString());
    } catch (err) {
      setIsConnected(false);
      setError(err instanceof Error ? err.message : "Unknown connection error");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refreshAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const visibleLineage = lineage.slice(0, 3);

  return (
    <main className="min-h-screen overflow-hidden bg-[var(--surface)] text-[var(--ink)]">
      <div className="absolute inset-0 -z-10 bg-orb" />

      <section className="mx-auto flex min-h-screen w-full max-w-[1680px] flex-col px-6 py-6 lg:px-10">
        <header className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="brand-mark">SD</div>
            <div>
              <div className="text-sm font-black tracking-tight">ShamsDAIS ERP Twin</div>
              <div className="text-xs text-[var(--muted)]">
                Trust Passport · Human-supervised AI operations
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-end gap-2">
            <span className={isConnected ? "status-pill success" : "status-pill danger"}>
              <Activity size={14} />
              {isConnected ? `API healthy · synced ${lastSync}` : "API or DB offline"}
            </span>
            <button className="refresh-button" onClick={refreshAll}>
              <RefreshCcw size={15} />
              Refresh
            </button>
          </div>
        </header>

        <section className="grid flex-1 grid-cols-1 gap-6 py-7 xl:grid-cols-[0.92fr_1.08fr]">
          <section className="hero-panel">
            <div className="tiny-label">Evidence-governed agentic ERP</div>

            <h1 className="hero-title">
              No AI action without a Trust Passport.
            </h1>

            <p className="hero-lead">
              ShamsDAIS turns every high-risk AI recommendation into a governed decision object:
              risk, evidence, lineage, and human approval must be attached before the ERP state can change.
            </p>

            <p className="hero-korean">
              연구실 운영 · 데이터 품질 · 모델 계보 · 인간 승인 기반 에이전트 ERP Twin
            </p>

            <div className="professor-strip">
              <FileCheck2 size={19} />
              <span>
                This is not a dashboard that explains decisions after they happen.
                It is an ERP gate that prevents AI from acting until the evidence is complete.
              </span>
            </div>

            <div className="mt-8 grid grid-cols-1 gap-3 md:grid-cols-3">
              <Principle
                icon={<ShieldCheck size={20} />}
                title="Monitor"
                text="Projects, data, models, equipment, budget, and publications become one live operational twin."
              />
              <Principle
                icon={<Fingerprint size={20} />}
                title="Detect"
                text="The Data Quality Firewall exposes broken ownership, lineage, budget, and reproducibility chains."
              />
              <Principle
                icon={<UserCheck size={20} />}
                title="Govern"
                text="AI recommendations become decision passports before any ERP state change."
              />
            </div>

            <div className="live-proof">
              <ProductMetric label="Projects" value={summary.projects} />
              <ProductMetric label="Datasets" value={summary.datasets} />
              <ProductMetric label="Risks" value={dq.total_issue_instances} />
              <ProductMetric label="AI proposals" value={summary.agent_proposals} />
            </div>
          </section>

          <section className="passport-stage">
            <div className="passport-glow" />

            <article className="trust-passport">
              <div className="passport-top">
                <div>
                  <div className="tiny-label">Decision Passport</div>
                  <div className="passport-id">{passport.id}</div>
                </div>
                <span className={`severity-pill ${severityClass(passport.severity)}`}>
                  {passport.severity === "high" || passport.severity === "critical"
                    ? "Human review required"
                    : passport.severity === "medium"
                      ? "Evidence check"
                      : "Trust passport"}
                </span>
              </div>

              <h2>{passport.title}</h2>

              <div className="passport-body">
                <PassportRow
                  icon={<Sparkles size={18} />}
                  label="AI proposal"
                  value={passport.aiProposal}
                />
                <PassportRow
                  icon={<Database size={18} />}
                  label="Evidence"
                  value={passport.evidence}
                />
                <PassportRow
                  icon={<LockKeyhole size={18} />}
                  label="Human approval gate"
                  value={passport.humanGate}
                />
                <PassportRow
                  icon={<BadgeCheck size={18} />}
                  label="Trust state"
                  value={passport.trustState}
                />
              </div>

              <div className="passport-actions">
                <button onClick={() => alert("Prototype action: approval event will be added in the next backend phase.")}>
                  Approve
                </button>
                <button className="ghost" onClick={() => alert("Prototype action: request-evidence workflow will be added next.")}>
                  Request evidence
                </button>
                <button className="ghost" onClick={() => alert("Prototype action: rejection reason and workflow ledger event will be added next.")}>
                  Reject
                </button>
              </div>
            </article>

            <div className="orbit-card data-card">
              <Database size={22} />
              <b>Data Vault</b>
              <span>{summary.datasets ?? "—"} datasets</span>
            </div>

            <div className="orbit-card agent-card">
              <Sparkles size={22} />
              <b>Agent Dock</b>
              <span>{summary.agent_proposals ?? "—"} proposals</span>
            </div>

            <div className="orbit-card gate-card">
              <LockKeyhole size={22} />
              <b>Approval Gate</b>
              <span>Human-controlled</span>
            </div>
          </section>
        </section>

        <section className="grid grid-cols-1 gap-5 pb-8 xl:grid-cols-[0.95fr_1.05fr]">
          <article className="glass-card">
            <div className="card-head">
              <div>
                <div className="tiny-label">Risk surface</div>
                <h3>Data Quality Firewall signals</h3>
              </div>
              <span className="status-pill info">
                <AlertTriangle size={14} />
                {dq.issue_types ?? "—"} issue types
              </span>
            </div>

            <div className="risk-list">
              {sortedIssues.length > 0 ? (
                sortedIssues.slice(0, 6).map((issue, index) => (
                  <button
                    key={`${issue.issue_id}-${index}`}
                    className={`risk-signal ${index === selectedIssueIndex ? "active" : ""}`}
                    onClick={() => setSelectedIssueIndex(index)}
                  >
                    <span className={`mini-severity ${severityClass(issue.severity)}`}>
                      {issue.severity || "risk"}
                    </span>
                    <span className="min-w-0 flex-1 text-left">
                      <b>{issue.title}</b>
                      <small>{shortText(issue.recommended_action, 120)}</small>
                    </span>
                    <strong>{issue.count ?? "—"}</strong>
                  </button>
                ))
              ) : (
                <div className="empty-state">
                  {isLoading ? "Loading firewall signals…" : "No firewall signals loaded."}
                </div>
              )}
            </div>
          </article>

          <article className="glass-card">
            <div className="card-head">
              <div>
                <div className="tiny-label">Research proof</div>
                <h3>Lineage evidence chain</h3>
              </div>
              <div className="project-input">
                <input
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  aria-label="Project ID"
                />
                <button onClick={() => loadLineage(projectId)}>Load proof</button>
              </div>
            </div>

            <div className="project-summary">
              <GitBranch size={18} />
              <div>
                <b>{project.project_code || projectId}</b>
                <span>
                  {project.title || "Project lineage proof will appear after synchronization."}
                </span>
              </div>
            </div>

            <div className="lineage-chain">
              {visibleLineage.length > 0 ? (
                visibleLineage.map((row, index) => (
                  <div className="lineage-row" key={`${row.experiment_code}-${index}`}>
                    <ChainNode label="Dataset" value={row.dataset_code} />
                    <ArrowRight className="chain-arrow" size={16} />
                    <ChainNode label="Model" value={row.model_code} />
                    <ArrowRight className="chain-arrow" size={16} />
                    <ChainNode label="Experiment" value={row.experiment_code} />
                    <ArrowRight className="chain-arrow" size={16} />
                    <ChainNode label="Publication" value={row.publication_title || "—"} />
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  {isLoading ? "Loading lineage proof…" : "No lineage proof loaded."}
                </div>
              )}
            </div>

            {topConflict && (
              <div className="conflict-strip">
                <AlertTriangle size={17} />
                <span>
                  Equipment conflict: <b>{topConflict.equipment_name || topConflict.equipment_id}</b>{" "}
                  · {topConflict.reservation_a} ↔ {topConflict.reservation_b}
                </span>
              </div>
            )}
          </article>
        </section>
      </section>
    </main>
  );
}

function Principle({
  icon,
  title,
  text,
}: {
  icon: React.ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="principle-card">
      <div>{icon}</div>
      <b>{title}</b>
      <span>{text}</span>
    </div>
  );
}

function PassportRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="passport-row">
      <div className="row-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <b>{value}</b>
      </div>
    </div>
  );
}

function ChainNode({ label, value }: { label: string; value?: string }) {
  return (
    <div className="chain-node">
      <span>{label}</span>
      <b>{shortText(value, 24)}</b>
    </div>
  );
}
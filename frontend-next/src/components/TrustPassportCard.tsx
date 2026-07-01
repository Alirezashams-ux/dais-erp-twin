import {
  BadgeCheck,
  Database,
  LockKeyhole,
  Sparkles,
} from "lucide-react";

export type DecisionPassport = {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  aiProposal: string;
  evidence: string;
  humanGate: string;
  trustState: string;
};

function severityClass(severity?: string) {
  const s = String(severity || "info").toLowerCase();
  if (s === "critical" || s === "high") return "danger";
  if (s === "medium") return "warning";
  if (s === "low") return "success";
  return "info";
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

export function TrustPassportCard({ passport }: { passport: DecisionPassport }) {
  return (
    <article className="trust-passport">
      <div className="passport-top">
        <div>
          <div className="tiny-label">Trust Passport</div>
          <div className="passport-id">{passport.id}</div>
        </div>

        <span className={`severity-pill ${severityClass(passport.severity)}`}>
          {passport.severity === "high" || passport.severity === "critical"
            ? "Human approval required"
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
  );
}

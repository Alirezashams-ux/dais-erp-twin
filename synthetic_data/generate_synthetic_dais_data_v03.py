"""
DAIS ERP Twin — Synthetic Data Generator v0.3 (skeleton)
=========================================================
Usage:
    python3 synthetic_data/generate_synthetic_dais_data_v03.py --mode normal
    python3 synthetic_data/generate_synthetic_dais_data_v03.py --mode stress

Output: synthetic_data/output_v03/
"""

import argparse
import csv
import hashlib
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="DAIS ERP Twin v0.3 generator")
    p.add_argument("--mode", choices=["normal", "stress"], default="normal",
                   help="normal=5-15%% anomaly rate, stress=30-60%%")
    return p.parse_args()


# ── Dirs ──────────────────────────────────────────────────────────────────────

def make_dirs(out: Path):
    (out / "raw").mkdir(parents=True, exist_ok=True)


# ── Utilities ─────────────────────────────────────────────────────────────────

def mid(prefix: str, n: int) -> str:
    return f"{prefix}-{n:04d}"


def rdate(start: date, end: date) -> date:
    d = (end - start).days
    return start + timedelta(days=random.randint(0, max(d, 1)))


def rdt(start: datetime, end: datetime) -> datetime:
    s = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, max(s, 1)))


def now_str() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def write_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ── Anomaly rate helper ───────────────────────────────────────────────────────

def rates(mode: str) -> dict:
    if mode == "stress":
        return dict(missing_owner=0.35, outdated_model=0.30, over_budget=0.40,
                    missing_pr=0.45, missing_proj=0.40, incomplete_lineage=0.35)
    return dict(missing_owner=0.08, outdated_model=0.06, over_budget=0.05,
                missing_pr=0.15, missing_proj=0.10, incomplete_lineage=0.15)


# ── A. People (v0.3 adds SYS-0001 SystemAgent) ───────────────────────────────

def generate_people(mode: str) -> list[dict]:
    research_areas = [
        "Industrial AI", "System-level anomaly detection", "Causality",
        "Data mining", "Machine learning", "Digital twin",
        "Manufacturing AI", "Computer vision", "Time-series analytics",
    ]
    people = []

    # SystemAgent identity (v0.3 new)
    people.append({
        "person_id": "SYS-0001",
        "display_name": "SystemAgent",
        "role": "SystemAgent",
        "degree": "",
        "email": "system_agent@synthetic.dais.local",
        "research_area": "Automated ERP Monitoring",
        "security_role": "SystemAgent",
        "actor_type": "SystemAgent",
    })

    # Professor
    people.append({
        "person_id": "P-0001",
        "display_name": "Professor_001",
        "role": "Professor",
        "degree": "",
        "email": "professor_001@synthetic.dais.local",
        "research_area": "Industrial AI, Causality, System-level anomaly detection",
        "security_role": "Professor",
        "actor_type": "Person",
    })

    for i in range(2, 4):
        people.append({
            "person_id": mid("P", i),
            "display_name": f"Admin_{i-1:03d}",
            "role": "Admin",
            "degree": "",
            "email": f"admin_{i-1:03d}@synthetic.dais.local",
            "research_area": "Lab operations",
            "security_role": "Admin",
            "actor_type": "Person",
        })

    for i in range(4, 16):
        deg = random.choice(["MS", "PhD"])
        people.append({
            "person_id": mid("P", i),
            "display_name": f"{deg}_Researcher_{i-3:03d}",
            "role": "GraduateResearcher",
            "degree": deg,
            "email": f"researcher_{i-3:03d}@synthetic.dais.local",
            "research_area": random.choice(research_areas),
            "security_role": "Researcher",
            "actor_type": "Person",
        })

    for i in range(16, 26):
        people.append({
            "person_id": mid("P", i),
            "display_name": f"OpenLab_Intern_{i-15:03d}",
            "role": "UndergraduateOpenLab",
            "degree": "BS",
            "email": f"openlab_{i-15:03d}@synthetic.dais.local",
            "research_area": random.choice(research_areas),
            "security_role": "Guest" if i % 3 == 0 else "Researcher",
            "actor_type": "Person",
        })

    return people


# ── B. Projects ───────────────────────────────────────────────────────────────

def generate_projects(mode: str) -> list[dict]:
    themes = [
        ("SYN-PJ-2026-BESS-SAFE",  "Battery Energy Storage System Safety Analytics",              "BESS safety AI"),
        ("SYN-PJ-2026-HYD-QM",     "Hydraulic Cylinder Quality Monitoring",                       "Hydraulic quality monitoring"),
        ("SYN-PJ-2026-WELD-NDT",   "Welding Defect Detection and NDT Intelligence",               "Welding inspection AI"),
        ("SYN-PJ-2026-ROBOT-CPS",  "CPS-Based Autonomous Robot Monitoring",                       "Cyber-physical systems"),
        ("SYN-PJ-2026-SEMI-DT",    "Digital Twin Simulation for Semiconductor Process Optimization","Semiconductor digital twin"),
        ("SYN-PJ-2026-PORT-DX",    "Port Process Mining and Digital Transformation",               "Process mining"),
        ("SYN-PJ-2026-MV-DEFECT",  "Machine Vision Defect Detection for Manufacturing",            "Machine vision"),
        ("SYN-PJ-2026-SYS-ANOM",   "System-Level Anomaly Detection for Industrial Operations",    "System anomaly detection"),
    ]
    projects = []
    for i, (code, title, theme) in enumerate(themes, 1):
        start = date(2026, random.randint(1, 3), random.randint(1, 20))
        end   = start + timedelta(days=random.randint(240, 720))
        budget = random.choice([50_000_000, 80_000_000, 120_000_000, 200_000_000, 300_000_000])
        projects.append({
            "project_id":       mid("PJ", i),
            "project_code":     code,
            "title":            title,
            "theme":            theme,
            "status":           random.choice(["active", "active", "active", "planning", "closing"]),
            "start_date":       start.isoformat(),
            "end_date":         end.isoformat(),
            "funding_agency":   random.choice([
                "Synthetic NRF", "Synthetic MSS", "Synthetic KIAT",
                "Synthetic Ulsan Industry Partner", "Synthetic Smart Manufacturing Program"]),
            "total_budget_krw": budget,
            "spent_krw":        int(budget * random.uniform(0.15, 0.72)),
            "pi_person_id":     "P-0001",
        })
    return projects


# ── C. Project members ────────────────────────────────────────────────────────

def generate_project_members(people: list, projects: list) -> list[dict]:
    researchers = [p for p in people if p["security_role"] in ("Researcher", "Professor")]
    rows = []
    for project in projects:
        rows.append({"project_id": project["project_id"], "person_id": "P-0001",
                     "project_role": "Principal Investigator", "allocation_percent": 20})
        for m in random.sample(researchers[1:], k=random.randint(3, 6)):
            rows.append({
                "project_id":      project["project_id"],
                "person_id":       m["person_id"],
                "project_role":    random.choice(["Lead Researcher", "Data Engineer",
                                                  "ML Engineer", "Experiment Owner"]),
                "allocation_percent": random.choice([20, 30, 40, 50, 60]),
            })
    return rows


# ── D. Equipment ──────────────────────────────────────────────────────────────

def generate_equipment(mode: str) -> list[dict]:
    categories = ["GPU Server", "Industrial Camera", "Edge AI Device",
                  "Sensor Kit", "Inspection Rig", "Storage Server", "Simulation Workstation"]
    rows = []
    for i in range(1, 21):
        cat = random.choice(categories)
        rows.append({
            "equipment_id":        mid("EQ", i),
            "asset_code":          f"ASSET-{cat.upper().replace(' ','-')}-{i:03d}",
            "name":                f"{cat}_{i:03d}",
            "category":            cat,
            "location":            random.choice(["DAIS Lab", "AI Server Room",
                                                  "Synthetic Factory Cell", "Shared Lab"]),
            "status":              random.choice(["available", "available", "available",
                                                  "maintenance", "reserved"]),
            "utilization_rate":    round(random.uniform(0.08, 0.92), 2),
            "maintenance_due_date":rdate(date(2026, 6, 1), date(2027, 3, 31)).isoformat(),
        })
    return rows


# ── E. Datasets ───────────────────────────────────────────────────────────────

def generate_datasets(projects: list, people: list, mode: str) -> list[dict]:
    r = rates(mode)
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    types = ["image", "sensor_time_series", "tabular", "simulation", "inspection_log"]
    rows = []
    for i in range(1, 51):
        pj = random.choice(projects)
        rows.append({
            "dataset_id":      mid("DS", i),
            "dataset_code":    f"DATA-{pj['theme'].upper().replace(' ','-')[:12]}-v{random.randint(1,4):02d}-{i:03d}",
            "project_id":      pj["project_id"],
            "owner_person_id": "" if random.random() < r["missing_owner"] else random.choice(researchers)["person_id"],
            "title":           f"Synthetic {pj['theme']} Dataset {i:03d}",
            "data_type":       random.choice(types),
            "version":         f"v{random.randint(1,4):02d}",
            "sensitivity_level": random.choice(["low", "medium", "medium", "high"]),
            "row_count":       random.randint(500, 500_000),
            "file_count":      random.randint(5, 5000),
            "quality_score":   round(random.uniform(0.55, 0.98), 2),
            "storage_path":    f"minio://synthetic-dais/datasets/DS-{i:04d}/",
            "approval_status": random.choice(["approved", "approved", "pending_review"]),
        })
    return rows


# ── F. Models ─────────────────────────────────────────────────────────────────

def generate_models(projects: list, datasets: list, mode: str) -> list[dict]:
    r = rates(mode)
    model_types = ["CNN", "LSTM", "Transformer", "XGBoost",
                   "NormalizingFlow", "RandomForest", "DigitalTwinSimulator"]
    rows = []
    for i in range(1, 41):
        pj = random.choice(projects)
        pj_ds = [d for d in datasets if d["project_id"] == pj["project_id"]] or datasets
        ds = random.choice(pj_ds)
        rows.append({
            "model_id":               mid("MDL", i),
            "model_code":             f"MODEL-{pj['theme'].upper().replace(' ','-')[:10]}-{i:03d}",
            "project_id":             pj["project_id"],
            "dataset_id":             ds["dataset_id"],
            "dataset_version":        ds["version"],
            "name":                   f"Synthetic {pj['theme']} Model {i:03d}",
            "model_type":             random.choice(model_types),
            "version":                f"v{random.randint(1,12):02d}",
            "dataset_version_status": "outdated" if random.random() < r["outdated_model"] else "current",
            "accuracy":               round(random.uniform(0.70, 0.99), 3),
            "f1_score":               round(random.uniform(0.65, 0.98), 3),
            "false_alarm_rate":       round(random.uniform(0.01, 0.18), 3),
            "deployment_status":      random.choice(["research", "demo", "pilot", "archived"]),
            "code_commit":            uuid4().hex[:12],
            "artifact_path":          f"minio://synthetic-dais/models/MDL-{i:04d}/",
            "hyperparameters":        json.dumps({"lr": round(random.uniform(1e-4, 1e-2), 5),
                                                  "epochs": random.randint(10, 100),
                                                  "batch_size": random.choice([16, 32, 64])}),
        })
    return rows


# ── G. Experiments (temporally consistent) ───────────────────────────────────

def generate_experiments(projects: list, datasets: list, models: list,
                          equipment: list, people: list, mode: str) -> list[dict]:
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    failure_reasons = [
        "OOM: GPU memory exceeded during training",
        "Dataset loader timeout after 3 retries",
        "Numerical instability — loss became NaN at epoch 12",
        "Experiment cancelled by researcher",
        "Equipment disconnected mid-run",
    ]
    rows = []
    for i in range(1, 121):
        pj = random.choice(projects)
        pj_m = [m for m in models if m["project_id"] == pj["project_id"]] or models
        mdl  = random.choice(pj_m)
        ds   = next((d for d in datasets if d["dataset_id"] == mdl["dataset_id"]),
                    random.choice(datasets))

        eq       = "" if random.random() < 0.04 else random.choice(equipment)["equipment_id"]
        status   = random.choice(["completed", "completed", "running", "failed", "pending"])
        pj_start = date.fromisoformat(pj["start_date"])
        earliest = datetime.combine(pj_start + timedelta(days=7), datetime.min.time())
        if earliest < datetime(2026, 3, 1):
            earliest = datetime(2026, 3, 1)
        latest   = datetime(2026, 8, 31)

        row = {
            "experiment_id":         mid("EXP", i),
            "experiment_code":       f"EXP-2026-{i:04d}",
            "project_id":            pj["project_id"],
            "dataset_id":            ds["dataset_id"],
            "model_id":              mdl["model_id"],
            "equipment_id":          eq,
            "researcher_person_id":  random.choice(researchers)["person_id"],
            "status":                status,
            "started_at":            "",
            "completed_at":          "",
            "failed_at":             "",
            "failure_reason":        "",
            "result_json":           "",
            "reproducibility_score": round(random.uniform(0.45, 0.98), 2),
        }
        if status == "running":
            row["started_at"] = rdt(earliest, latest).isoformat()
        elif status == "completed":
            s = rdt(earliest, latest)
            row["started_at"]   = s.isoformat()
            row["completed_at"] = (s + timedelta(hours=random.randint(2, 120))).isoformat()
            row["result_json"]  = json.dumps({"loss": round(random.uniform(0.01, 0.45), 4),
                                              "accuracy": round(random.uniform(0.70, 0.99), 3)})
        elif status == "failed":
            s = rdt(earliest, latest)
            row["started_at"]    = s.isoformat()
            row["failed_at"]     = (s + timedelta(hours=random.randint(1, 48))).isoformat()
            row["failure_reason"]= random.choice(failure_reasons)
        rows.append(row)
    return rows


# ── H. Equipment reservations + algorithmic conflict detection ────────────────

def generate_equipment_reservations(equipment: list, experiments: list) -> list[dict]:
    rows = []
    for i in range(1, 61):
        eq  = random.choice(equipment)
        exp = random.choice(experiments)
        s   = datetime(2026, 7, random.randint(1, 20), random.choice([9, 10, 13, 14]), 0)
        e   = s + timedelta(hours=random.choice([2, 3, 4, 6]))
        rows.append({
            "reservation_id":         mid("RSV", i),
            "equipment_id":           eq["equipment_id"],
            "experiment_id":          exp["experiment_id"],
            "reserved_by_person_id":  exp["researcher_person_id"],
            "start_time":             s.isoformat(),
            "end_time":               e.isoformat(),
            "status":                 random.choice(["confirmed", "confirmed", "pending"]),
        })
    # Inject one guaranteed overlap pair
    conflict_eq = equipment[0]["equipment_id"]
    rows.append({"reservation_id": mid("RSV", 901), "equipment_id": conflict_eq,
                 "experiment_id": experiments[0]["experiment_id"],
                 "reserved_by_person_id": experiments[0]["researcher_person_id"],
                 "start_time": "2026-07-15T10:00:00", "end_time": "2026-07-15T14:00:00",
                 "status": "confirmed"})
    rows.append({"reservation_id": mid("RSV", 902), "equipment_id": conflict_eq,
                 "experiment_id": experiments[1]["experiment_id"],
                 "reserved_by_person_id": experiments[1]["researcher_person_id"],
                 "start_time": "2026-07-15T12:00:00", "end_time": "2026-07-15T16:00:00",
                 "status": "confirmed"})
    return rows


def detect_equipment_conflicts(reservations: list[dict]) -> list[tuple]:
    """Algorithmic overlap detection — no hardcoded IDs."""
    conflicts = []
    confirmed = [r for r in reservations if r["status"] == "confirmed"]
    from itertools import combinations
    for a, b in combinations(confirmed, 2):
        if a["equipment_id"] != b["equipment_id"]:
            continue
        s1, e1 = datetime.fromisoformat(a["start_time"]), datetime.fromisoformat(a["end_time"])
        s2, e2 = datetime.fromisoformat(b["start_time"]), datetime.fromisoformat(b["end_time"])
        if s1 < e2 and s2 < e1:          # overlap condition
            conflicts.append((a["reservation_id"], b["reservation_id"], a["equipment_id"]))
    return conflicts


# ── I. Purchases (status-driven, reconciled) ──────────────────────────────────

def generate_purchases(projects: list, people: list, mode: str) -> list[dict]:
    r = rates(mode)
    items = ["Industrial camera lens", "GPU workstation component", "Vibration sensor kit",
             "Thermal camera module", "NAS storage expansion", "Annotation software license",
             "Edge AI box", "Pressure sensor", "Experiment fixture", "Conference registration"]
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    rows = []
    for i in range(1, 81):
        pj         = random.choice(projects)
        over_budget= random.random() < r["over_budget"]
        amount     = random.randint(100_000, 6_000_000)
        if over_budget:
            amount = int(pj["total_budget_krw"]) + random.randint(1_000_000, 10_000_000)

        # Status consistent with amount and over_budget flag
        if over_budget:
            status = random.choice(["pending", "rejected"])
        else:
            status = random.choice(["pending", "approved", "approved",
                                    "ordered", "received", "invoiced", "paid"])
        rows.append({
            "purchase_request_id":  mid("PR", i),
            "request_code":         f"PR-2026-{i:04d}",
            "project_id":           pj["project_id"],
            "requester_person_id":  random.choice(researchers)["person_id"],
            "item_name":            random.choice(items),
            "amount_krw":           amount,
            "status":               status,
            "approval_required":    "true" if amount >= 1_000_000 else "false",
            "budget_check_status":  "over_budget" if over_budget else "ok",
            "created_at":           (datetime(2026, 4, 1) + timedelta(days=random.randint(0, 160))).isoformat(),
        })
    return rows


# ── J. Invoices ───────────────────────────────────────────────────────────────

def generate_invoices(projects: list, purchases: list, mode: str) -> list[dict]:
    r = rates(mode)
    suppliers = ["Ulsan Sensor Co.", "Ulsan Sensors Ltd.", "Korea Vision Systems",
                 "Busan Industrial AI Tools", "Daejeon Simulation Works",
                 "Seoul GPU Market", "Gyeongnam Robotics Parts", "Synthetic Data Services Korea"]
    rows = []
    for i in range(1, 91):
        pr      = random.choice(purchases)
        m_proj  = random.random() < r["missing_proj"]
        m_pr    = random.random() < r["missing_pr"]
        amount  = int(pr["amount_krw"]) if random.random() < 0.75 else random.randint(100_000, 8_000_000)
        rows.append({
            "invoice_id":             mid("INV", i),
            "invoice_code":           f"INV-2026-{i:04d}",
            "supplier_name":          random.choice(suppliers),
            "business_registration_no": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10000,99999)}",
            "project_id":             "" if m_proj else pr["project_id"],
            "purchase_request_id":    "" if m_pr   else pr["purchase_request_id"],
            "amount_krw":             amount,
            "vat_krw":                int(amount * 0.10),
            "issue_date":             rdate(date(2026, 4, 1), date(2026, 10, 31)).isoformat(),
            "source_file":            f"synthetic_invoice_{i:04d}.pdf",
            "confidence":             round(random.uniform(0.55, 0.98), 2),
        })
    return rows


# ── K. Milestones ─────────────────────────────────────────────────────────────

def generate_milestones(projects: list) -> list[dict]:
    rows = []
    for i in range(1, 41):
        pj = random.choice(projects)
        rows.append({
            "milestone_id":   mid("MS", i),
            "project_id":     pj["project_id"],
            "milestone_name": random.choice(["Interim report", "Dataset release",
                                              "Model evaluation", "Prototype demo",
                                              "Final report", "Paper submission"]),
            "due_date":       rdate(date(2026, 7, 1), date(2027, 5, 31)).isoformat(),
            "status":         random.choice(["not_started", "in_progress", "completed", "delayed"]),
            "risk_score":     round(random.uniform(0.05, 0.95), 2),
        })
    return rows


# ── L. Publications ───────────────────────────────────────────────────────────

def generate_publications(projects: list, datasets: list, models: list,
                           experiments: list, mode: str) -> list[dict]:
    r = rates(mode)
    rows = []
    for i in range(1, 31):
        pj       = random.choice(projects)
        pj_m     = [m for m in models if m["project_id"] == pj["project_id"]] or models
        mdl      = random.choice(pj_m)
        pj_e     = [e for e in experiments if e["model_id"] == mdl["model_id"]]
        exp      = random.choice(pj_e) if pj_e else random.choice(experiments)
        missing  = random.random() < r["incomplete_lineage"]

        # synthetic author list
        authors = ", ".join([f"Author_{random.randint(1,20):03d}" for _ in range(random.randint(2, 5))])

        rows.append({
            "publication_id":               mid("PUB", i),
            "title":                        f"Synthetic Paper {i:03d}: {pj['theme']} with AI-Based Analytics",
            "project_id":                   pj["project_id"],
            "dataset_id":                   "" if missing else mdl["dataset_id"],
            "model_id":                     "" if missing else mdl["model_id"],
            "experiment_id":                "" if missing else exp["experiment_id"],
            "authors":                      authors,
            "type":                         random.choice(["journal", "conference", "technical_report"]),
            "status":                       random.choice(["idea", "draft", "submitted", "accepted", "published"]),
            "target_venue":                 random.choice(["Synthetic Journal of Industrial AI",
                                                           "Synthetic KIIE Conference",
                                                           "Synthetic IEEE Venue"]),
            "year":                         random.choice([2026, 2027]),
            "reproducibility_package_status": "incomplete" if missing else random.choice(["complete", "complete", "pending"]),
            "doi_like_id":                  f"10.9999/synth.dais.2026.{i:04d}",
            "code_commit":                  "" if missing else uuid4().hex[:12],
            "artifact_path":                "" if missing else f"minio://synthetic-dais/publications/PUB-{i:04d}/",
        })
    return rows


# ── M. ERP event ledger (hash-chained) ───────────────────────────────────────

def generate_erp_events(projects, datasets, models, experiments, purchases, invoices) -> list[dict]:
    events, prev = [], "GENESIS"
    for items, etype, itype in [
        (projects,    "ProjectCreated",     "Project"),
        (datasets,    "DatasetRegistered",  "Dataset"),
        (models,      "ModelRegistered",    "ModelAsset"),
        (experiments, "ExperimentRecorded", "Experiment"),
        (purchases,   "PurchaseRequested",  "PurchaseRequest"),
        (invoices,    "InvoiceReceived",    "Invoice"),
    ]:
        for item in items:
            eid = list(item.values())[0]
            core = {"event_type": etype, "entity_type": itype,
                    "entity_id": eid, "payload": item, "previous_hash": prev}
            h = sha256(core)
            events.append({
                "event_id":    str(uuid4()),
                "event_type":  etype,
                "entity_type": itype,
                "entity_id":   eid,
                "payload":     item,
                "source_uri":  "synthetic_generator_v03",
                "confidence":  round(random.uniform(0.80, 0.99), 2),
                "created_by":  "SYS-0001",
                "actor_type":  "SystemAgent",
                "previous_hash": prev,
                "event_hash":  h,
                "created_at":  now_str(),
            })
            prev = h
    return events


# ── N. Agent proposals (with algorithmic conflict detection) ──────────────────

def generate_agent_proposals(datasets, models, reservations, purchases,
                              invoices, publications, conflicts) -> list[dict]:
    proposals = []

    def add(ptype, title, etype, eid, risk, conf, evidence):
        proposals.append({
            "proposal_id":          mid("AP", len(proposals) + 1),
            "proposal_type":        ptype,
            "title":                title,
            "affected_entity_type": etype,
            "affected_entity_id":   eid,
            "risk_level":           risk,
            "confidence":           conf,
            "evidence":             evidence,
            "status":               "pending",
            "created_by":           "SYS-0001",
            "actor_type":           "SystemAgent",
            "created_at":           now_str(),
            "requires_approval":    True,
        })

    for inv in invoices:
        if not inv["project_id"]:
            add("LINK_INVOICE_TO_PROJECT",
                f"Invoice {inv['invoice_code']} has no linked project",
                "Invoice", inv["invoice_id"], "medium", inv["confidence"],
                ["project_id is empty", inv["source_file"], f"supplier={inv['supplier_name']}"])

    for ds in datasets:
        if not ds["owner_person_id"]:
            add("ASSIGN_DATASET_OWNER",
                f"Dataset {ds['dataset_code']} has no owner",
                "Dataset", ds["dataset_id"], "medium", 0.91,
                ["owner_person_id is empty", f"project_id={ds['project_id']}"])

    for m in models:
        if m["dataset_version_status"] == "outdated":
            add("REVIEW_MODEL_DATASET_VERSION",
                f"Model {m['model_code']} uses an outdated dataset version",
                "ModelAsset", m["model_id"], "high", 0.88,
                ["dataset_version_status=outdated", f"dataset_id={m['dataset_id']}"])

    for pr in purchases:
        if pr["budget_check_status"] == "over_budget":
            add("REVIEW_OVER_BUDGET_PURCHASE",
                f"Purchase request {pr['request_code']} exceeds project budget",
                "PurchaseRequest", pr["purchase_request_id"], "high", 0.95,
                ["budget_check_status=over_budget", f"amount_krw={pr['amount_krw']}"])

    for pub in publications:
        if pub["reproducibility_package_status"] == "incomplete":
            add("FIX_PUBLICATION_LINEAGE",
                f"Publication {pub['publication_id']} has incomplete reproducibility lineage",
                "Publication", pub["publication_id"], "medium", 0.83,
                ["missing dataset/model/experiment link", f"project_id={pub['project_id']}"])

    # Algorithmically detected equipment conflicts
    for rsv_a, rsv_b, eq_id in conflicts:
        add("RESOLVE_EQUIPMENT_CONFLICT",
            f"Overlap detected: {rsv_a} and {rsv_b} on {eq_id}",
            "EquipmentReservation", rsv_a, "high", 0.96,
            [f"equipment_id={eq_id}", f"conflicts_with={rsv_b}"])

    return proposals


# ── O1. Workflow events (hash-chained, purchase lifecycle) ────────────────────

LIFECYCLE_STEPS = {
    "pending":  ["PurchaseRequested", "AdminReviewed"],
    "approved": ["PurchaseRequested", "AdminReviewed", "ProfessorApproved"],
    "rejected": ["PurchaseRequested", "AdminReviewed", "ProfessorRejected"],
    "ordered":  ["PurchaseRequested", "AdminReviewed", "ProfessorApproved",
                 "OrderPlaced"],
    "received": ["PurchaseRequested", "AdminReviewed", "ProfessorApproved",
                 "OrderPlaced", "GoodsReceived"],
    "invoiced": ["PurchaseRequested", "AdminReviewed", "ProfessorApproved",
                 "OrderPlaced", "GoodsReceived", "InvoiceReceived", "InvoiceMatched"],
    "paid":     ["PurchaseRequested", "AdminReviewed", "ProfessorApproved",
                 "OrderPlaced", "GoodsReceived", "InvoiceReceived", "InvoiceMatched",
                 "PaymentCompleted"],
}


def _actor_for_step(event_type: str, requester_id: str, people: list) -> tuple:
    """Return (actor_id, actor_type, role) for a workflow step."""
    professor = next(p for p in people if p["role"] == "Professor")
    admins    = [p for p in people if p["role"] == "Admin"]
    if event_type == "PurchaseRequested":
        actor = next((p for p in people if p["person_id"] == requester_id), people[1])
        return actor["person_id"], actor["actor_type"], actor["role"]
    if event_type in ("AdminReviewed", "OrderPlaced", "GoodsReceived",
                      "InvoiceReceived", "PaymentCompleted"):
        a = random.choice(admins)
        return a["person_id"], a["actor_type"], a["role"]
    if event_type in ("ProfessorApproved", "ProfessorRejected"):
        return professor["person_id"], professor["actor_type"], professor["role"]
    if event_type == "InvoiceMatched":
        return "SYS-0001", "SystemAgent", "SystemAgent"
    return requester_id, "Person", "Researcher"


def generate_workflow_events(purchases: list, people: list) -> list:
    """Hash-chained workflow events following the purchase lifecycle."""
    events, prev, counter = [], "GENESIS", 1
    for pr in purchases:
        steps   = LIFECYCLE_STEPS.get(pr["status"], ["PurchaseRequested"])
        base_ts = datetime.fromisoformat(pr["created_at"])
        for step_i, event_type in enumerate(steps):
            ts = (base_ts + timedelta(hours=step_i * random.randint(2, 24))).isoformat()
            actor_id, actor_type, role = _actor_for_step(
                event_type, pr["requester_person_id"], people)
            payload = {
                "purchase_request_id": pr["purchase_request_id"],
                "item_name":           pr["item_name"],
                "amount_krw":          pr["amount_krw"],
                "project_id":          pr["project_id"],
                "step":                step_i + 1,
            }
            core = {"event_type": event_type, "entity_type": "PurchaseRequest",
                    "entity_id":  pr["purchase_request_id"],
                    "payload":    payload, "previous_hash": prev}
            h = sha256(core)
            events.append({
                "workflow_event_id": mid("WEV", counter),
                "event_type":        event_type,
                "entity_type":       "PurchaseRequest",
                "entity_id":         pr["purchase_request_id"],
                "actor_id":          actor_id,
                "actor_type":        actor_type,
                "role":              role,
                "payload":           payload,
                "timestamp":         ts,
                "previous_hash":     prev,
                "event_hash":        h,
            })
            prev = h
            counter += 1
    return events


def validate_workflow_chain(workflow_events: list) -> tuple:
    """Returns (chain_valid, mismatch_count, chain_break_count)."""
    mismatches, breaks, prev = 0, 0, "GENESIS"
    for ev in workflow_events:
        if ev["previous_hash"] != prev:
            breaks += 1
        core = {"event_type": ev["event_type"], "entity_type": ev["entity_type"],
                "entity_id":  ev["entity_id"], "payload": ev["payload"],
                "previous_hash": ev["previous_hash"]}
        if sha256(core) != ev["event_hash"]:
            mismatches += 1
        prev = ev["event_hash"]
    return (mismatches == 0 and breaks == 0), mismatches, breaks


_WF_MUST_HAVE = {
    "pending":  set(),
    "approved": {"ProfessorApproved"},
    "rejected": {"ProfessorRejected"},
    "ordered":  {"OrderPlaced"},
    "received": {"GoodsReceived"},
    "invoiced": {"InvoiceReceived", "InvoiceMatched"},
    "paid":     {"PaymentCompleted"},
}
_WF_MUST_NOT = {
    "pending": {"ProfessorApproved", "ProfessorRejected"},
}


def reconcile_purchase_workflow(purchases: list, workflow_events: list) -> dict:
    """Validate each purchase_request's status against its workflow events."""
    pr_events: dict = {}
    for ev in workflow_events:
        pr_events.setdefault(ev["entity_id"], set()).add(ev["event_type"])
    mismatches = []
    for pr in purchases:
        pr_id  = pr["purchase_request_id"]
        status = pr["status"]
        evset  = pr_events.get(pr_id, set())
        missing  = _WF_MUST_HAVE.get(status, set()) - evset
        unwanted = _WF_MUST_NOT.get(status, set()) & evset
        if missing or unwanted:
            mismatches.append({
                "purchase_request_id": pr_id,
                "status":              status,
                "missing_events":      sorted(missing),
                "unexpected_events":   sorted(unwanted),
            })
    return {
        "purchase_workflow_status_mismatches":        len(mismatches),
        "purchase_workflow_status_mismatch_examples": mismatches[:5],
    }


# ── O. Simple quality report ──────────────────────────────────────────────────

def generate_quality_report(mode, datasets, models, purchases, invoices,
                              publications, reservations, experiments,
                              erp_events, conflicts,
                              workflow_events=None) -> dict:
    anomalies = []

    def add_a(atype, entity, eid, severity):
        anomalies.append({"type": atype, "entity": entity, "id": eid, "severity": severity})

    for d in datasets:
        if not d["owner_person_id"]:
            add_a("MISSING_DATASET_OWNER", "Dataset", d["dataset_id"], "medium")
    for m in models:
        if m["dataset_version_status"] == "outdated":
            add_a("OUTDATED_DATASET_VERSION", "ModelAsset", m["model_id"], "high")
    for pr in purchases:
        if pr["budget_check_status"] == "over_budget":
            add_a("OVER_BUDGET_PURCHASE", "PurchaseRequest", pr["purchase_request_id"], "high")
    for inv in invoices:
        if not inv["project_id"]:
            add_a("UNLINKED_INVOICE_NO_PROJECT", "Invoice", inv["invoice_id"], "medium")
        if not inv["purchase_request_id"]:
            add_a("UNLINKED_INVOICE_NO_PR", "Invoice", inv["invoice_id"], "medium")
    for pub in publications:
        if pub["reproducibility_package_status"] == "incomplete":
            add_a("INCOMPLETE_PUB_LINEAGE", "Publication", pub["publication_id"], "medium")
    for rsv_a, rsv_b, eq_id in conflicts:
        add_a("EQUIPMENT_DOUBLE_BOOKING", "EquipmentReservation", rsv_a, "high")

    # Temporal consistency check
    temporal_errors = []
    for e in experiments:
        if e["status"] == "pending" and (e["started_at"] or e["completed_at"]):
            temporal_errors.append(e["experiment_id"])
        if e["status"] == "completed":
            if not e["started_at"] or not e["completed_at"]:
                temporal_errors.append(e["experiment_id"])
            elif e["started_at"] >= e["completed_at"]:
                temporal_errors.append(e["experiment_id"])

    # Hash-chain validation
    chain_ok = True
    prev = "GENESIS"
    for ev in erp_events:
        core = {"event_type": ev["event_type"], "entity_type": ev["entity_type"],
                "entity_id": ev["entity_id"], "payload": ev["payload"],
                "previous_hash": prev}
        expected = sha256(core)
        if expected != ev["event_hash"]:
            chain_ok = False
            break
        prev = ev["event_hash"]

    by_type = {}
    by_sev  = {"low": 0, "medium": 0, "high": 0}
    for a in anomalies:
        by_type[a["type"]] = by_type.get(a["type"], 0) + 1
        by_sev[a["severity"]] += 1

    # Workflow chain validation & purchase reconciliation
    wf_count             = len(workflow_events) if workflow_events else 0
    wf_chain_valid       = None
    wf_mismatches        = None
    wf_breaks            = None
    pr_mismatches        = None
    pr_mismatch_examples = []
    if workflow_events:
        wf_chain_valid, wf_mismatches, wf_breaks = validate_workflow_chain(workflow_events)
        recon = reconcile_purchase_workflow(purchases, workflow_events)
        pr_mismatches        = recon["purchase_workflow_status_mismatches"]
        pr_mismatch_examples = recon["purchase_workflow_status_mismatch_examples"]

    return {
        "version":               "v0.3",
        "mode":                  mode,
        "generated_at":          now_str(),
        "total_anomalies":       len(anomalies),
        "by_type":               by_type,
        "by_severity":           by_sev,
        "temporal_errors":       temporal_errors,
        "erp_chain_valid":       chain_ok,
        "equipment_conflicts":   len(conflicts),
        "workflow_event_count":                       wf_count,
        "workflow_hash_chain_valid":                  wf_chain_valid,
        "workflow_hash_mismatches":                   wf_mismatches,
        "workflow_chain_breaks":                      wf_breaks,
        "purchase_workflow_status_mismatches":        pr_mismatches,
        "purchase_workflow_status_mismatch_examples": pr_mismatch_examples,
        "anomalies":             anomalies,
    }


# ── P. Summary ────────────────────────────────────────────────────────────────

def generate_summary(mode, counts, dq) -> dict:
    return {
        "version":    "v0.3",
        "mode":       mode,
        "generated_at": now_str(),
        "counts":     counts,
        "total_anomalies":       dq["total_anomalies"],
        "anomaly_severity":      dq["by_severity"],
        "erp_chain_valid":       dq["erp_chain_valid"],
        "equipment_conflicts":   dq["equipment_conflicts"],
        "temporal_errors":       len(dq["temporal_errors"]),
        "workflow_event_count":                dq.get("workflow_event_count"),
        "workflow_hash_chain_valid":           dq.get("workflow_hash_chain_valid"),
        "purchase_workflow_status_mismatches": dq.get("purchase_workflow_status_mismatches"),
    }


# ── Q. Main ───────────────────────────────────────────────────────────────────

def main():
    args   = parse_args()
    mode   = args.mode
    random.seed(42)

    OUT = Path("synthetic_data/output_v03")
    make_dirs(OUT)

    print(f"[v0.3] mode={mode}  output={OUT.resolve()}")

    # Generate
    print("  generating entities ...")
    people       = generate_people(mode)
    projects     = generate_projects(mode)
    members      = generate_project_members(people, projects)
    equipment    = generate_equipment(mode)
    datasets     = generate_datasets(projects, people, mode)
    models       = generate_models(projects, datasets, mode)
    experiments  = generate_experiments(projects, datasets, models, equipment, people, mode)
    reservations = generate_equipment_reservations(equipment, experiments)
    conflicts    = detect_equipment_conflicts(reservations)
    purchases    = generate_purchases(projects, people, mode)
    invoices     = generate_invoices(projects, purchases, mode)
    milestones   = generate_milestones(projects)
    publications = generate_publications(projects, datasets, models, experiments, mode)
    erp_events      = generate_erp_events(projects, datasets, models, experiments, purchases, invoices)
    workflow_events = generate_workflow_events(purchases, people)
    proposals       = generate_agent_proposals(datasets, models, reservations, purchases,
                                                invoices, publications, conflicts)

    # Write CSVs / JSONL / JSON
    print("  writing files ...")
    write_csv(OUT / "people.csv",                 people)
    write_csv(OUT / "projects.csv",               projects)
    write_csv(OUT / "project_members.csv",        members)
    write_csv(OUT / "equipment.csv",              equipment)
    write_csv(OUT / "datasets.csv",               datasets)
    write_csv(OUT / "model_assets.csv",           models)
    write_csv(OUT / "experiments.csv",            experiments)
    write_csv(OUT / "equipment_reservations.csv", reservations)
    write_csv(OUT / "purchase_requests.csv",      purchases)
    write_csv(OUT / "invoices.csv",               invoices)
    write_csv(OUT / "milestones.csv",             milestones)
    write_csv(OUT / "publications.csv",           publications)
    write_jsonl(OUT / "erp_events.jsonl",          erp_events)
    write_jsonl(OUT / "workflow_events.jsonl",     workflow_events)
    write_json(OUT / "agent_proposals.json",      proposals)

    # Reports
    dq = generate_quality_report(mode, datasets, models, purchases, invoices,
                                  publications, reservations, experiments,
                                  erp_events, conflicts,
                                  workflow_events=workflow_events)
    counts = {
        "people": len(people), "projects": len(projects),
        "project_members": len(members), "equipment": len(equipment),
        "datasets": len(datasets), "model_assets": len(models),
        "experiments": len(experiments), "equipment_reservations": len(reservations),
        "purchase_requests": len(purchases), "invoices": len(invoices),
        "milestones": len(milestones), "publications": len(publications),
        "erp_events": len(erp_events), "workflow_events": len(workflow_events),
        "agent_proposals": len(proposals),
    }
    summary = generate_summary(mode, counts, dq)
    write_json(OUT / "data_quality_report_v03.json",  dq)
    write_json(OUT / "generation_summary_v03.json",   summary)

    # Print
    print("\n" + "=" * 58)
    print(f"  DAIS ERP Twin v0.3  [{mode.upper()} mode]")
    print("=" * 58)
    for k, v in counts.items():
        print(f"  {k:<32} {v:>5}")
    print(f"\n  Equipment conflicts detected : {len(conflicts)}")
    print(f"  Total anomalies injected    : {dq['total_anomalies']}")
    print(f"  Severity  high / medium     : {dq['by_severity']['high']} / {dq['by_severity']['medium']}")
    print(f"  ERP event chain valid       : {dq['erp_chain_valid']}")
    print(f"  Workflow chain valid        : {dq['workflow_hash_chain_valid']}")
    print(f"  Purchase-workflow mismatches: {dq['purchase_workflow_status_mismatches']}")
    print(f"  Temporal errors             : {len(dq['temporal_errors'])}")
    print(f"  Output dir                  : {OUT.resolve()}")
    print("=" * 58)


if __name__ == "__main__":
    main()

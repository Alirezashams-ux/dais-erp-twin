"""
DAIS ERP Twin — Synthetic Data Generator v0.2
==============================================
Deterministic (random.seed(42)), modular, safe to run locally.

Preserves all v0.1 schemas and IDs.  Adds:
  - Temporal realism for experiments
  - Workflow events (purchase, dataset, model, proposal pipelines)
  - Security & audit layer (approvals, audit_logs, access_attempts,
    role_permissions, prompt_history, security_events)
  - Raw file manifest (invoice PDFs, budget Excel, experiment logs,
    training logs, meeting notes)
  - DAIS operational modules (lectures, off-campus talks, recruiting,
    OpenLab activities, achievements, student skills)
  - Domain-specific project data (BESS sensor logs, welding images,
    hydraulic logs, semiconductor sim runs, port event logs,
    anomaly records)
  - generation_summary_v02.json + data_quality_report_v02.json
"""

import csv
import json
import random
import hashlib
from uuid import uuid4
from pathlib import Path
from datetime import datetime, timedelta, date, timezone

random.seed(42)

OUT_DIR = Path("synthetic_data/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── A. Utilities ──────────────────────────────────────────────────────────────

def make_id(prefix: str, n: int) -> str:
    return f"{prefix}-{n:04d}"


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta))


def random_dt(start: datetime, end: datetime) -> datetime:
    delta = int((end - start).total_seconds())
    if delta <= 0:
        return start
    return start + timedelta(seconds=random.randint(0, delta))


def utcnow_str() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_csv(filename: str, rows: list[dict]):
    if not rows:
        return
    path = OUT_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(filename: str, rows: list[dict]):
    path = OUT_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def write_json(filename: str, data):
    path = OUT_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ── B. v0.1 Generators (preserved + temporal fixes in experiments) ────────────

def generate_people():
    research_areas = [
        "Industrial AI",
        "System-level anomaly detection",
        "Causality",
        "Data mining",
        "Machine learning",
        "Digital twin",
        "Manufacturing AI",
        "Computer vision",
        "Time-series analytics",
    ]

    people = []

    people.append({
        "person_id": "P-0001",
        "display_name": "Professor_001",
        "role": "Professor",
        "degree": "",
        "email": "professor_001@synthetic.dais.local",
        "research_area": "Industrial AI, Causality, System-level anomaly detection",
        "security_role": "Professor",
    })

    for i in range(2, 4):
        people.append({
            "person_id": make_id("P", i),
            "display_name": f"Admin_{i-1:03d}",
            "role": "Admin",
            "degree": "",
            "email": f"admin_{i-1:03d}@synthetic.dais.local",
            "research_area": "Lab operations",
            "security_role": "Admin",
        })

    for i in range(4, 16):
        degree = random.choice(["MS", "PhD"])
        people.append({
            "person_id": make_id("P", i),
            "display_name": f"{degree}_Researcher_{i-3:03d}",
            "role": "GraduateResearcher",
            "degree": degree,
            "email": f"researcher_{i-3:03d}@synthetic.dais.local",
            "research_area": random.choice(research_areas),
            "security_role": "Researcher",
        })

    for i in range(16, 26):
        people.append({
            "person_id": make_id("P", i),
            "display_name": f"OpenLab_Intern_{i-15:03d}",
            "role": "UndergraduateOpenLab",
            "degree": "BS",
            "email": f"openlab_{i-15:03d}@synthetic.dais.local",
            "research_area": random.choice(research_areas),
            "security_role": "Guest" if i % 3 == 0 else "Researcher",
        })

    return people


def generate_projects():
    themes = [
        ("SYN-PJ-2026-BESS-SAFE",  "Battery Energy Storage System Safety Analytics",        "BESS safety AI"),
        ("SYN-PJ-2026-HYD-QM",     "Hydraulic Cylinder Quality Monitoring",                "Hydraulic quality monitoring"),
        ("SYN-PJ-2026-WELD-NDT",   "Welding Defect Detection and NDT Intelligence",        "Welding inspection AI"),
        ("SYN-PJ-2026-ROBOT-CPS",  "CPS-Based Autonomous Robot Monitoring",                "Cyber-physical systems"),
        ("SYN-PJ-2026-SEMI-DT",    "Digital Twin Simulation for Semiconductor Process Optimization", "Semiconductor digital twin"),
        ("SYN-PJ-2026-PORT-DX",    "Port Process Mining and Digital Transformation",       "Process mining"),
        ("SYN-PJ-2026-MV-DEFECT",  "Machine Vision Defect Detection for Manufacturing",    "Machine vision"),
        ("SYN-PJ-2026-SYS-ANOM",   "System-Level Anomaly Detection for Industrial Operations", "System anomaly detection"),
    ]

    projects = []
    for i, (code, title, theme) in enumerate(themes, start=1):
        start = date(2026, random.randint(1, 3), random.randint(1, 20))
        end = start + timedelta(days=random.randint(240, 720))
        budget = random.choice([50_000_000, 80_000_000, 120_000_000, 200_000_000, 300_000_000])

        projects.append({
            "project_id": make_id("PJ", i),
            "project_code": code,
            "title": title,
            "theme": theme,
            "status": random.choice(["active", "active", "active", "planning", "closing"]),
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "funding_agency": random.choice([
                "Synthetic NRF",
                "Synthetic MSS",
                "Synthetic KIAT",
                "Synthetic Ulsan Industry Partner",
                "Synthetic Smart Manufacturing Program",
            ]),
            "total_budget_krw": budget,
            "spent_krw": int(budget * random.uniform(0.15, 0.72)),
            "pi_person_id": "P-0001",
        })

    return projects


def generate_project_members(people, projects):
    researchers = [p for p in people if p["security_role"] in ["Researcher", "Professor"]]
    rows = []

    for project in projects:
        rows.append({
            "project_id": project["project_id"],
            "person_id": "P-0001",
            "project_role": "Principal Investigator",
            "allocation_percent": 20,
        })

        members = random.sample(researchers[1:], k=random.randint(3, 6))
        for m in members:
            rows.append({
                "project_id": project["project_id"],
                "person_id": m["person_id"],
                "project_role": random.choice(["Lead Researcher", "Data Engineer", "ML Engineer", "Experiment Owner"]),
                "allocation_percent": random.choice([20, 30, 40, 50, 60]),
            })

    return rows


def generate_equipment():
    categories = [
        "GPU Server",
        "Industrial Camera",
        "Edge AI Device",
        "Sensor Kit",
        "Inspection Rig",
        "Storage Server",
        "Simulation Workstation",
    ]

    equipment = []
    for i in range(1, 21):
        category = random.choice(categories)
        equipment.append({
            "equipment_id": make_id("EQ", i),
            "asset_code": f"ASSET-{category.upper().replace(' ', '-')}-{i:03d}",
            "name": f"{category}_{i:03d}",
            "category": category,
            "location": random.choice(["DAIS Lab", "AI Server Room", "Synthetic Factory Cell", "Shared Lab"]),
            "status": random.choice(["available", "available", "available", "maintenance", "reserved"]),
            "utilization_rate": round(random.uniform(0.08, 0.92), 2),
            "maintenance_due_date": random_date(date(2026, 6, 1), date(2027, 3, 31)).isoformat(),
        })

    return equipment


def generate_datasets(projects, people):
    dataset_types = ["image", "sensor_time_series", "tabular", "simulation", "inspection_log"]
    rows = []

    researchers = [p for p in people if p["security_role"] == "Researcher"]

    for i in range(1, 51):
        project = random.choice(projects)
        missing_owner = random.random() < 0.08

        rows.append({
            "dataset_id": make_id("DS", i),
            "dataset_code": f"DATA-{project['theme'].upper().replace(' ', '-')[:12]}-v{random.randint(1, 4):02d}-{i:03d}",
            "project_id": project["project_id"],
            "owner_person_id": "" if missing_owner else random.choice(researchers)["person_id"],
            "title": f"Synthetic {project['theme']} Dataset {i:03d}",
            "data_type": random.choice(dataset_types),
            "version": f"v{random.randint(1, 4):02d}",
            "sensitivity_level": random.choice(["low", "medium", "medium", "high"]),
            "row_count": random.randint(500, 500_000),
            "file_count": random.randint(5, 5000),
            "quality_score": round(random.uniform(0.55, 0.98), 2),
            "storage_path": f"minio://synthetic-dais/datasets/DS-{i:04d}/",
            "approval_status": random.choice(["approved", "approved", "pending_review"]),
        })

    return rows


def generate_models(projects, datasets):
    model_types = ["CNN", "LSTM", "Transformer", "XGBoost", "NormalizingFlow", "RandomForest", "DigitalTwinSimulator"]
    rows = []

    for i in range(1, 41):
        project = random.choice(projects)
        project_datasets = [d for d in datasets if d["project_id"] == project["project_id"]]
        dataset = random.choice(project_datasets or datasets)
        outdated = random.random() < 0.06

        rows.append({
            "model_id": make_id("MDL", i),
            "model_code": f"MODEL-{project['theme'].upper().replace(' ', '-')[:10]}-{i:03d}",
            "project_id": project["project_id"],
            "dataset_id": dataset["dataset_id"],
            "name": f"Synthetic {project['theme']} Model {i:03d}",
            "model_type": random.choice(model_types),
            "version": f"v{random.randint(1, 12):02d}",
            "dataset_version_status": "outdated" if outdated else "current",
            "accuracy": round(random.uniform(0.70, 0.99), 3),
            "f1_score": round(random.uniform(0.65, 0.98), 3),
            "false_alarm_rate": round(random.uniform(0.01, 0.18), 3),
            "deployment_status": random.choice(["research", "demo", "pilot", "archived"]),
            "code_commit": uuid4().hex[:12],
        })

    return rows


def generate_experiments(projects, datasets, models, equipment, people):
    """
    v0.2 FIX — Temporal realism:
      pending  → no started_at, no completed_at
      running  → started_at only
      completed→ started_at < completed_at
      failed   → started_at + failed_at + failure_reason
    No experiment starts before its project start_date.
    """
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    failure_reasons = [
        "OOM: GPU memory exceeded during training",
        "Dataset loader timeout after 3 retries",
        "Numerical instability — loss became NaN at epoch 12",
        "Experiment cancelled by researcher",
        "Equipment disconnected mid-run",
        "Hyperparameter config validation error",
    ]
    rows = []

    for i in range(1, 121):
        project = random.choice(projects)
        project_models = [m for m in models if m["project_id"] == project["project_id"]]
        model = random.choice(project_models or models)
        dataset = next((d for d in datasets if d["dataset_id"] == model["dataset_id"]), random.choice(datasets))

        missing_equipment = random.random() < 0.04
        eq = "" if missing_equipment else random.choice(equipment)["equipment_id"]

        status = random.choice(["completed", "completed", "running", "failed", "pending"])

        # Earliest start = max(project start + 7 days, 2026-03-01)
        proj_start = date.fromisoformat(project["start_date"])
        earliest = datetime.combine(proj_start + timedelta(days=7), datetime.min.time())
        if earliest < datetime(2026, 3, 1):
            earliest = datetime(2026, 3, 1)
        latest_start = datetime(2026, 8, 31)

        result = {
            "loss": round(random.uniform(0.01, 0.45), 4),
            "accuracy": round(random.uniform(0.70, 0.99), 3),
            "notes": "synthetic experiment result",
        }

        row = {
            "experiment_id": make_id("EXP", i),
            "experiment_code": f"EXP-2026-{i:04d}",
            "project_id": project["project_id"],
            "dataset_id": dataset["dataset_id"],
            "model_id": model["model_id"],
            "equipment_id": eq,
            "researcher_person_id": random.choice(researchers)["person_id"],
            "status": status,
            "started_at": "",
            "completed_at": "",
            "failed_at": "",
            "failure_reason": "",
            "result_json": "",
            "reproducibility_score": round(random.uniform(0.45, 0.98), 2),
        }

        if status == "pending":
            pass  # all date fields remain empty

        elif status == "running":
            row["started_at"] = random_dt(earliest, latest_start).isoformat()

        elif status == "completed":
            started = random_dt(earliest, latest_start)
            completed = started + timedelta(hours=random.randint(2, 120))
            row["started_at"] = started.isoformat()
            row["completed_at"] = completed.isoformat()
            row["result_json"] = json.dumps(result)

        elif status == "failed":
            started = random_dt(earliest, latest_start)
            failed = started + timedelta(hours=random.randint(1, 48))
            row["started_at"] = started.isoformat()
            row["failed_at"] = failed.isoformat()
            row["failure_reason"] = random.choice(failure_reasons)

        rows.append(row)

    return rows


def generate_equipment_reservations(equipment, experiments):
    rows = []

    for i in range(1, 61):
        eq = random.choice(equipment)
        exp = random.choice(experiments)
        start = datetime(2026, 7, random.randint(1, 20), random.choice([9, 10, 13, 14]), 0)
        end = start + timedelta(hours=random.choice([2, 3, 4, 6]))

        rows.append({
            "reservation_id": make_id("RSV", i),
            "equipment_id": eq["equipment_id"],
            "experiment_id": exp["experiment_id"],
            "reserved_by_person_id": exp["researcher_person_id"],
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "status": random.choice(["confirmed", "confirmed", "pending"]),
        })

    # Intentional double-booking conflict (hard-coded)
    conflict_eq = equipment[0]["equipment_id"]
    rows.append({
        "reservation_id": make_id("RSV", 901),
        "equipment_id": conflict_eq,
        "experiment_id": experiments[0]["experiment_id"],
        "reserved_by_person_id": experiments[0]["researcher_person_id"],
        "start_time": "2026-07-15T10:00:00",
        "end_time": "2026-07-15T14:00:00",
        "status": "confirmed",
    })
    rows.append({
        "reservation_id": make_id("RSV", 902),
        "equipment_id": conflict_eq,
        "experiment_id": experiments[1]["experiment_id"],
        "reserved_by_person_id": experiments[1]["researcher_person_id"],
        "start_time": "2026-07-15T12:00:00",
        "end_time": "2026-07-15T16:00:00",
        "status": "confirmed",
    })

    return rows


def generate_purchases(projects, people):
    items = [
        "Industrial camera lens",
        "GPU workstation component",
        "Vibration sensor kit",
        "Thermal camera module",
        "NAS storage expansion",
        "Annotation software license",
        "Edge AI box",
        "Pressure sensor",
        "Experiment fixture",
        "Conference registration",
    ]

    researchers = [p for p in people if p["security_role"] == "Researcher"]
    rows = []

    for i in range(1, 81):
        project = random.choice(projects)
        over_budget = random.random() < 0.05

        amount = random.randint(100_000, 6_000_000)
        if over_budget:
            amount = int(project["total_budget_krw"]) + random.randint(1_000_000, 10_000_000)

        rows.append({
            "purchase_request_id": make_id("PR", i),
            "request_code": f"PR-2026-{i:04d}",
            "project_id": project["project_id"],
            "requester_person_id": random.choice(researchers)["person_id"],
            "item_name": random.choice(items),
            "amount_krw": amount,
            "status": random.choice(["pending", "approved", "approved", "rejected"]),
            "approval_required": "true" if amount >= 1_000_000 else "false",
            "budget_check_status": "over_budget" if over_budget else "ok",
            "created_at": (datetime(2026, 4, 1) + timedelta(days=random.randint(0, 160))).isoformat(),
        })

    return rows


def generate_invoices(projects, purchase_requests):
    suppliers = [
        "Ulsan Sensor Co.",
        "Ulsan Sensors Ltd.",
        "Korea Vision Systems",
        "Busan Industrial AI Tools",
        "Daejeon Simulation Works",
        "Seoul GPU Market",
        "Gyeongnam Robotics Parts",
        "Synthetic Data Services Korea",
    ]

    rows = []

    for i in range(1, 91):
        pr = random.choice(purchase_requests)
        missing_project = random.random() < 0.10
        missing_pr = random.random() < 0.15

        amount = int(pr["amount_krw"]) if random.random() < 0.75 else random.randint(100_000, 8_000_000)
        vat = int(amount * 0.10)

        rows.append({
            "invoice_id": make_id("INV", i),
            "invoice_code": f"INV-2026-{i:04d}",
            "supplier_name": random.choice(suppliers),
            "business_registration_no": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10000,99999)}",
            "project_id": "" if missing_project else pr["project_id"],
            "purchase_request_id": "" if missing_pr else pr["purchase_request_id"],
            "amount_krw": amount,
            "vat_krw": vat,
            "issue_date": random_date(date(2026, 4, 1), date(2026, 10, 31)).isoformat(),
            "source_file": f"synthetic_invoice_{i:04d}.pdf",
            "confidence": round(random.uniform(0.55, 0.98), 2),
        })

    return rows


def generate_milestones(projects):
    rows = []

    for i in range(1, 41):
        project = random.choice(projects)
        due = random_date(date(2026, 7, 1), date(2027, 5, 31))
        risk = round(random.uniform(0.05, 0.95), 2)

        rows.append({
            "milestone_id": make_id("MS", i),
            "project_id": project["project_id"],
            "milestone_name": random.choice([
                "Interim report",
                "Dataset release",
                "Model evaluation",
                "Prototype demo",
                "Final report",
                "Paper submission",
            ]),
            "due_date": due.isoformat(),
            "status": random.choice(["not_started", "in_progress", "completed", "delayed"]),
            "risk_score": risk,
        })

    return rows


def generate_publications(projects, datasets, models, experiments):
    rows = []

    for i in range(1, 31):
        project = random.choice(projects)
        project_models = [m for m in models if m["project_id"] == project["project_id"]]
        model = random.choice(project_models or models)

        project_experiments = [e for e in experiments if e["model_id"] == model["model_id"]]
        exp = random.choice(project_experiments) if project_experiments else random.choice(experiments)

        missing_lineage = random.random() < 0.15

        rows.append({
            "publication_id": make_id("PUB", i),
            "title": f"Synthetic Paper {i:03d}: {project['theme']} with AI-Based Analytics",
            "project_id": project["project_id"],
            "dataset_id": "" if missing_lineage else model["dataset_id"],
            "model_id": "" if missing_lineage else model["model_id"],
            "experiment_id": "" if missing_lineage else exp["experiment_id"],
            "type": random.choice(["journal", "conference", "technical_report"]),
            "status": random.choice(["idea", "draft", "submitted", "accepted", "published"]),
            "target_venue": random.choice([
                "Synthetic Journal of Industrial AI",
                "Synthetic KIIE Conference",
                "Synthetic IEEE Venue",
            ]),
            "year": random.choice([2026, 2027]),
            "reproducibility_package_status": "incomplete" if missing_lineage else random.choice(["complete", "complete", "pending"]),
        })

    return rows


def _create_chain_event(event_type, entity_type, entity_id, payload, previous_hash):
    raw = json.dumps({
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": payload,
        "previous_hash": previous_hash,
    }, sort_keys=True, default=str)

    event_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": payload,
        "source_uri": "synthetic_generator",
        "confidence": round(random.uniform(0.80, 0.99), 2),
        "created_by": "SystemSyntheticGenerator",
        "previous_hash": previous_hash,
        "event_hash": event_hash,
        "created_at": utcnow_str(),
    }


def generate_events(projects, datasets, models, experiments, purchases, invoices):
    """Hash-chained ERP event ledger (same as v0.1, replaces erp_events.jsonl)."""
    events = []
    prev = "GENESIS"

    for obj, etype, itype in [
        (projects,   "ProjectCreated",      "Project"),
        (datasets,   "DatasetRegistered",   "Dataset"),
        (models,     "ModelRegistered",     "ModelAsset"),
        (experiments,"ExperimentRecorded",  "Experiment"),
        (purchases,  "PurchaseRequested",   "PurchaseRequest"),
        (invoices,   "InvoiceReceived",     "Invoice"),
    ]:
        for item in obj:
            ev = _create_chain_event(etype, itype, item[list(item.keys())[0]], item, prev)
            events.append(ev)
            prev = ev["event_hash"]

    return events


def generate_agent_proposals(datasets, models, equipment_reservations, purchases, invoices, publications):
    proposals = []

    def add(proposal_type, title, entity_type, entity_id, risk, confidence, evidence):
        proposals.append({
            "proposal_id": make_id("AP", len(proposals) + 1),
            "proposal_type": proposal_type,
            "title": title,
            "affected_entity_type": entity_type,
            "affected_entity_id": entity_id,
            "risk_level": risk,
            "confidence": confidence,
            "evidence": evidence,
            "status": "pending",
            "created_at": utcnow_str(),
            "requires_approval": True,
        })

    for inv in invoices:
        if inv["project_id"] == "":
            add("LINK_INVOICE_TO_PROJECT",
                f"Invoice {inv['invoice_code']} has no linked project",
                "Invoice", inv["invoice_id"], "medium", inv["confidence"],
                ["project_id is empty", inv["source_file"], f"supplier={inv['supplier_name']}"])

    for ds in datasets:
        if ds["owner_person_id"] == "":
            add("ASSIGN_DATASET_OWNER",
                f"Dataset {ds['dataset_code']} has no owner",
                "Dataset", ds["dataset_id"], "medium", 0.91,
                ["owner_person_id is empty", f"project_id={ds['project_id']}"])

    for model in models:
        if model["dataset_version_status"] == "outdated":
            add("REVIEW_MODEL_DATASET_VERSION",
                f"Model {model['model_code']} uses an outdated dataset version",
                "ModelAsset", model["model_id"], "high", 0.88,
                ["dataset_version_status=outdated", f"dataset_id={model['dataset_id']}"])

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

    conflict_ids = {"RSV-0901", "RSV-0902"}
    for r in equipment_reservations:
        if r["reservation_id"] in conflict_ids:
            add("RESOLVE_EQUIPMENT_CONFLICT",
                f"Equipment conflict detected for reservation {r['reservation_id']}",
                "EquipmentReservation", r["reservation_id"], "high", 0.96,
                [f"equipment_id={r['equipment_id']}",
                 f"start_time={r['start_time']}",
                 f"end_time={r['end_time']}"])

    return proposals


# ── C. v0.2 Workflow Events ───────────────────────────────────────────────────

def generate_workflow_events(people, projects, datasets, models, experiments, purchases, invoices, proposals):
    """
    Fine-grained per-entity workflow step events.
    Covers: purchase pipeline, invoice pipeline, dataset lifecycle,
            model lifecycle, and proposal review cycle.
    Stored separately as workflow_events.jsonl (not hash-chained).
    """
    events = []
    idx = 1

    admin   = next(p for p in people if p["role"] == "Admin")
    prof    = next(p for p in people if p["role"] == "Professor")
    researchers = [p for p in people if p["security_role"] == "Researcher"]

    def wev(step, entity_type, entity_id, actor_id, actor_role, payload=None, ts=None):
        nonlocal idx
        events.append({
            "workflow_event_id": make_id("WEV", idx),
            "step": step,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "actor_person_id": actor_id,
            "actor_role": actor_role,
            "payload": payload or {},
            "timestamp": ts or utcnow_str(),
        })
        idx += 1

    # ── Purchase → Invoice pipeline ──────────────────────────────────────────
    for pr in purchases:
        base = datetime.fromisoformat(pr["created_at"])

        wev("PurchaseRequested", "PurchaseRequest", pr["purchase_request_id"],
            pr["requester_person_id"], "Researcher",
            {"item": pr["item_name"], "amount_krw": pr["amount_krw"]},
            base.isoformat())

        review_dt = base + timedelta(days=random.randint(1, 3))
        needs_prof = pr["approval_required"] == "true"
        wev("AdminReviewed", "PurchaseRequest", pr["purchase_request_id"],
            admin["person_id"], "Admin",
            {"forwarded_to_professor": needs_prof,
             "budget_check": pr["budget_check_status"]},
            review_dt.isoformat())

        if needs_prof:
            approve_dt = review_dt + timedelta(days=random.randint(1, 2))
            decision = "approved" if pr["status"] == "approved" else "rejected"
            step = "ProfessorApproved" if decision == "approved" else "ProfessorRejected"
            wev(step, "PurchaseRequest", pr["purchase_request_id"],
                prof["person_id"], "Professor",
                {"decision": decision, "over_budget": pr["budget_check_status"] == "over_budget"},
                approve_dt.isoformat())

        if pr["status"] == "approved":
            order_dt = review_dt + timedelta(days=random.randint(2, 5))
            wev("OrderPlaced", "PurchaseRequest", pr["purchase_request_id"],
                admin["person_id"], "Admin", {}, order_dt.isoformat())

            goods_dt = order_dt + timedelta(days=random.randint(5, 20))
            wev("GoodsReceived", "PurchaseRequest", pr["purchase_request_id"],
                pr["requester_person_id"], "Researcher", {}, goods_dt.isoformat())

    for inv in invoices:
        base = datetime.strptime(inv["issue_date"], "%Y-%m-%d").replace(hour=9)
        wev("InvoiceReceived", "Invoice", inv["invoice_id"],
            admin["person_id"], "Admin",
            {"supplier": inv["supplier_name"], "amount_krw": inv["amount_krw"]},
            base.isoformat())

        if inv["purchase_request_id"]:
            matched_dt = base + timedelta(days=random.randint(1, 3))
            wev("InvoiceMatched", "Invoice", inv["invoice_id"],
                admin["person_id"], "Admin",
                {"purchase_request_id": inv["purchase_request_id"]},
                matched_dt.isoformat())

            payment_dt = matched_dt + timedelta(days=random.randint(3, 14))
            wev("PaymentCompleted", "Invoice", inv["invoice_id"],
                admin["person_id"], "Admin",
                {"total_krw": inv["amount_krw"] + inv["vat_krw"]},
                payment_dt.isoformat())

    # ── Dataset lifecycle ────────────────────────────────────────────────────
    for ds in datasets:
        owner_id = ds["owner_person_id"] or random.choice(researchers)["person_id"]
        base = datetime(2026, 3, random.randint(1, 28), random.randint(8, 17))

        wev("DatasetCreated", "Dataset", ds["dataset_id"],
            owner_id, "Researcher", {"title": ds["title"]}, base.isoformat())

        upload_dt = base + timedelta(hours=random.randint(1, 48))
        wev("DatasetUploaded", "Dataset", ds["dataset_id"],
            owner_id, "Researcher",
            {"storage_path": ds["storage_path"], "file_count": ds["file_count"]},
            upload_dt.isoformat())

        qc_dt = upload_dt + timedelta(days=random.randint(1, 5))
        wev("DatasetQualityChecked", "Dataset", ds["dataset_id"],
            "SystemAgent", "SystemAgent",
            {"quality_score": ds["quality_score"], "row_count": ds["row_count"]},
            qc_dt.isoformat())

        if ds["owner_person_id"] == "":
            assign_dt = qc_dt + timedelta(days=random.randint(1, 7))
            wev("DatasetOwnerAssigned", "Dataset", ds["dataset_id"],
                admin["person_id"], "Admin",
                {"assigned_to": owner_id}, assign_dt.isoformat())

        version_dt = qc_dt + timedelta(days=random.randint(2, 10))
        wev("DatasetVersionReleased", "Dataset", ds["dataset_id"],
            owner_id, "Researcher",
            {"version": ds["version"]}, version_dt.isoformat())

        if ds["approval_status"] == "approved":
            approved_dt = version_dt + timedelta(days=random.randint(1, 5))
            wev("DatasetApprovedForTraining", "Dataset", ds["dataset_id"],
                prof["person_id"], "Professor",
                {"sensitivity_level": ds["sensitivity_level"]},
                approved_dt.isoformat())

    # ── Model lifecycle ──────────────────────────────────────────────────────
    for mdl in models:
        researcher = random.choice(researchers)
        base = datetime(2026, 4, random.randint(1, 28), random.randint(8, 18))

        wev("TrainingStarted", "ModelAsset", mdl["model_id"],
            researcher["person_id"], "Researcher",
            {"model_type": mdl["model_type"], "dataset_id": mdl["dataset_id"]},
            base.isoformat())

        train_done = base + timedelta(hours=random.randint(2, 72))
        wev("TrainingCompleted", "ModelAsset", mdl["model_id"],
            "SystemAgent", "SystemAgent",
            {"accuracy": mdl["accuracy"], "f1_score": mdl["f1_score"]},
            train_done.isoformat())

        eval_dt = train_done + timedelta(hours=random.randint(1, 24))
        wev("EvaluationCompleted", "ModelAsset", mdl["model_id"],
            researcher["person_id"], "Researcher",
            {"false_alarm_rate": mdl["false_alarm_rate"]},
            eval_dt.isoformat())

        reg_dt = eval_dt + timedelta(hours=random.randint(1, 12))
        wev("ModelRegistered", "ModelAsset", mdl["model_id"],
            researcher["person_id"], "Researcher",
            {"deployment_status": mdl["deployment_status"],
             "code_commit": mdl["code_commit"]},
            reg_dt.isoformat())

    # Wire experiments to models
    for exp in experiments:
        if exp["status"] == "completed":
            wev("ModelUsedInExperiment", "Experiment", exp["experiment_id"],
                exp["researcher_person_id"], "Researcher",
                {"model_id": exp["model_id"], "dataset_id": exp["dataset_id"]},
                exp.get("completed_at") or utcnow_str())

    # ── Proposal review cycle ────────────────────────────────────────────────
    for prop in proposals:
        base = datetime.fromisoformat(prop["created_at"][:19])
        wev("ProposalCreated", "AgentProposal", prop["proposal_id"],
            "SystemAgent", "SystemAgent",
            {"proposal_type": prop["proposal_type"], "risk_level": prop["risk_level"]},
            base.isoformat())

        if prop["risk_level"] == "high":
            review_dt = base + timedelta(days=random.randint(1, 3))
            outcome = random.choice(["ProposalApproved", "ProposalApproved", "ProposalRejected"])
            wev(outcome, "AgentProposal", prop["proposal_id"],
                prof["person_id"], "Professor",
                {"evidence_count": len(prop["evidence"])},
                review_dt.isoformat())

            if outcome == "ProposalApproved":
                fix_dt = review_dt + timedelta(days=random.randint(1, 5))
                wev("CorrectionApplied", "AgentProposal", prop["proposal_id"],
                    random.choice(researchers)["person_id"], "Researcher",
                    {"corrected_entity": prop["affected_entity_id"]},
                    fix_dt.isoformat())
        else:
            # Medium-risk: admin can self-approve
            review_dt = base + timedelta(days=random.randint(1, 4))
            wev("ProposalApproved", "AgentProposal", prop["proposal_id"],
                admin["person_id"], "Admin", {}, review_dt.isoformat())

    return events


# ── D. v0.2 Security & Audit ──────────────────────────────────────────────────

def generate_role_permissions():
    """Static role-permission matrix for the DAIS ERP system."""
    matrix = [
        # role, entity_type, action, permission
        ("Professor",    "Dataset",          "read",     "allow"),
        ("Professor",    "Dataset",          "approve",  "allow"),
        ("Professor",    "ModelAsset",       "read",     "allow"),
        ("Professor",    "PurchaseRequest",  "approve",  "allow"),
        ("Professor",    "AgentProposal",    "approve",  "allow"),
        ("Professor",    "AgentProposal",    "reject",   "allow"),
        ("Admin",        "Dataset",          "read",     "allow"),
        ("Admin",        "PurchaseRequest",  "review",   "allow"),
        ("Admin",        "Invoice",          "match",    "allow"),
        ("Admin",        "Invoice",          "pay",      "allow"),
        ("Admin",        "AgentProposal",    "read",     "allow"),
        ("Researcher",   "Dataset",          "read",     "allow"),
        ("Researcher",   "Dataset",          "create",   "allow"),
        ("Researcher",   "Dataset",          "upload",   "allow"),
        ("Researcher",   "ModelAsset",       "create",   "allow"),
        ("Researcher",   "Experiment",       "create",   "allow"),
        ("Researcher",   "PurchaseRequest",  "create",   "allow"),
        ("Researcher",   "Dataset_high",     "read",     "deny"),
        ("Guest",        "Dataset",          "read",     "allow"),
        ("Guest",        "Dataset_high",     "read",     "deny"),
        ("Guest",        "Dataset_medium",   "read",     "deny"),
        ("Guest",        "ModelAsset",       "create",   "deny"),
        ("Guest",        "PurchaseRequest",  "create",   "deny"),
        ("SystemAgent",  "Dataset",          "read",     "allow"),
        ("SystemAgent",  "AgentProposal",    "create",   "allow"),
        ("SystemAgent",  "AgentProposal",    "approve",  "deny"),   # agent never self-approves
        ("SystemAgent",  "PurchaseRequest",  "approve",  "deny"),
        ("SystemAgent",  "Invoice",          "pay",      "deny"),
    ]
    return [
        {
            "permission_id": make_id("PERM", i + 1),
            "role": role,
            "entity_type": entity_type,
            "action": action,
            "permission": permission,
        }
        for i, (role, entity_type, action, permission) in enumerate(matrix)
    ]


def generate_access_attempts(people, datasets):
    """
    Simulate access attempts:
      - legitimate researcher reads
      - guest denied on high/medium sensitivity datasets
      - SystemAgent read-only scans
    """
    rows = []
    guests      = [p for p in people if p["security_role"] == "Guest"]
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    high_ds     = [d for d in datasets if d["sensitivity_level"] == "high"]
    med_ds      = [d for d in datasets if d["sensitivity_level"] == "medium"]

    # Legitimate researcher reads (30)
    for i in range(1, 31):
        researcher = random.choice(researchers)
        ds = random.choice(datasets)
        rows.append({
            "attempt_id": make_id("ACC", i),
            "actor_person_id": researcher["person_id"],
            "actor_role": "Researcher",
            "resource_type": "Dataset",
            "resource_id": ds["dataset_id"],
            "sensitivity_level": ds["sensitivity_level"],
            "timestamp": (datetime(2026, 5, random.randint(1, 31), random.randint(8, 20),
                                   random.randint(0, 59))).isoformat(),
            "result": "granted",
            "ip_address": f"192.168.1.{random.randint(10, 99)}",
        })

    # Guest denied (20)
    targets = (high_ds + med_ds) or datasets
    for i in range(31, 51):
        actor = random.choice(guests) if guests else random.choice(researchers)
        ds = random.choice(targets)
        rows.append({
            "attempt_id": make_id("ACC", i),
            "actor_person_id": actor["person_id"],
            "actor_role": "Guest",
            "resource_type": "Dataset",
            "resource_id": ds["dataset_id"],
            "sensitivity_level": ds["sensitivity_level"],
            "timestamp": (datetime(2026, 5, random.randint(1, 31), random.randint(8, 20),
                                   random.randint(0, 59))).isoformat(),
            "result": "denied",
            "ip_address": f"10.0.0.{random.randint(1, 50)}",
        })

    # SystemAgent scans (20)
    for i in range(51, 71):
        ds = random.choice(datasets)
        rows.append({
            "attempt_id": make_id("ACC", i),
            "actor_person_id": "SystemAgent",
            "actor_role": "SystemAgent",
            "resource_type": "Dataset",
            "resource_id": ds["dataset_id"],
            "sensitivity_level": ds["sensitivity_level"],
            "timestamp": (datetime(2026, 5, random.randint(1, 31), random.randint(8, 20),
                                   random.randint(0, 59))).isoformat(),
            "result": "granted",
            "ip_address": "127.0.0.1",
        })

    return rows


def generate_approval_records(people, purchases, datasets, proposals):
    """Approval chain records for purchases, datasets, and high-risk proposals."""
    rows = []
    admin = next(p for p in people if p["role"] == "Admin")
    prof  = next(p for p in people if p["role"] == "Professor")

    # Purchase approval chain
    for pr in purchases:
        if pr["approval_required"] == "true":
            rows.append({
                "approval_id": make_id("APR", len(rows) + 1),
                "entity_type": "PurchaseRequest",
                "entity_id": pr["purchase_request_id"],
                "action": "AdminReview",
                "actor_person_id": admin["person_id"],
                "actor_role": "Admin",
                "decision": "forwarded",
                "decision_reason": "Amount ≥ ₩1,000,000 — requires professor sign-off",
                "timestamp": (datetime.fromisoformat(pr["created_at"]) + timedelta(days=2)).isoformat(),
            })
            decision = pr["status"] if pr["status"] != "pending" else "pending"
            rows.append({
                "approval_id": make_id("APR", len(rows) + 1),
                "entity_type": "PurchaseRequest",
                "entity_id": pr["purchase_request_id"],
                "action": "ProfessorApproval",
                "actor_person_id": prof["person_id"],
                "actor_role": "Professor",
                "decision": decision,
                "decision_reason": f"Budget check: {pr['budget_check_status']}",
                "timestamp": (datetime.fromisoformat(pr["created_at"]) + timedelta(days=4)).isoformat(),
            })

    # Dataset training approval
    for ds in datasets:
        if ds["approval_status"] == "approved":
            rows.append({
                "approval_id": make_id("APR", len(rows) + 1),
                "entity_type": "Dataset",
                "entity_id": ds["dataset_id"],
                "action": "DatasetApproval",
                "actor_person_id": prof["person_id"],
                "actor_role": "Professor",
                "decision": "approved",
                "decision_reason": f"Quality score {ds['quality_score']} acceptable for training",
                "timestamp": datetime(2026, 4, random.randint(1, 28)).isoformat(),
            })

    # High-risk agent proposal approval
    for prop in proposals:
        if prop["risk_level"] == "high":
            decision = random.choice(["approved", "approved", "rejected"])
            rows.append({
                "approval_id": make_id("APR", len(rows) + 1),
                "entity_type": "AgentProposal",
                "entity_id": prop["proposal_id"],
                "action": "ProposalReview",
                "actor_person_id": prof["person_id"],
                "actor_role": "Professor",
                "decision": decision,
                "decision_reason": f"Risk={prop['risk_level']}, Confidence={prop['confidence']}",
                "timestamp": (datetime.fromisoformat(prop["created_at"][:19]) + timedelta(days=2)).isoformat(),
            })

    return rows


def generate_audit_logs(people, access_attempts, approval_records, datasets):
    """Fine-grained audit log for every significant system action."""
    logs = []
    researchers = [p for p in people if p["security_role"] == "Researcher"]

    def log(actor_id, actor_role, action, entity_type, entity_id,
            result="success", metadata=None, ts=None):
        logs.append({
            "log_id": str(uuid4()),
            "actor_person_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "result": result,
            "metadata": metadata or {},
            "ip_address": f"192.168.1.{random.randint(1, 200)}",
            "timestamp": ts or utcnow_str(),
        })

    for a in access_attempts:
        log(a["actor_person_id"], a["actor_role"],
            "READ", a["resource_type"], a["resource_id"],
            "success" if a["result"] == "granted" else "denied",
            {"sensitivity_level": a["sensitivity_level"]},
            a["timestamp"])

    for apr in approval_records:
        log(apr["actor_person_id"], apr["actor_role"],
            apr["action"], apr["entity_type"], apr["entity_id"],
            apr["decision"], {}, apr["timestamp"])

    for ds in datasets[:20]:
        researcher = random.choice(researchers)
        log(researcher["person_id"], "Researcher",
            "UPLOAD", "Dataset", ds["dataset_id"],
            "success", {"file_count": ds["file_count"]})

    return logs


def generate_security_events(people, access_attempts, proposals):
    """Security events: access denials, policy violations, high-risk proposals."""
    events = []
    denied = [a for a in access_attempts if a["result"] == "denied"]

    for i, attempt in enumerate(denied, start=1):
        events.append({
            "security_event_id": make_id("SEC", i),
            "event_type": "ACCESS_DENIED",
            "actor_person_id": attempt["actor_person_id"],
            "actor_role": attempt["actor_role"],
            "description": (
                f"Access denied: {attempt['resource_type']} {attempt['resource_id']} "
                f"(sensitivity={attempt['sensitivity_level']})"
            ),
            "severity": "medium",
            "timestamp": attempt["timestamp"],
            "resolution": "policy_enforced",
        })

    # SystemAgent self-approval attempt — blocked
    events.append({
        "security_event_id": make_id("SEC", len(events) + 1),
        "event_type": "POLICY_VIOLATION_BLOCKED",
        "actor_person_id": "SystemAgent",
        "actor_role": "SystemAgent",
        "description": "SystemAgent attempted to self-approve AgentProposal AP-0001 — blocked by role_permissions policy",
        "severity": "high",
        "timestamp": "2026-05-15T14:32:11+00:00",
        "resolution": "blocked",
    })

    # High-risk proposals flagged for human review
    high_risk = [p for p in proposals if p["risk_level"] == "high"]
    for prop in high_risk[:5]:
        events.append({
            "security_event_id": make_id("SEC", len(events) + 1),
            "event_type": "HIGH_RISK_PROPOSAL_FLAGGED",
            "actor_person_id": "SystemAgent",
            "actor_role": "SystemAgent",
            "description": f"Proposal {prop['proposal_id']} ({prop['proposal_type']}) requires professor approval",
            "severity": "high",
            "timestamp": prop["created_at"][:19] + "+00:00",
            "resolution": "pending_professor_review",
        })

    return events


def generate_prompt_history(people, proposals, datasets):
    """Synthetic agent prompt/response history (no sensitive payloads)."""
    logs = []
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    prof        = next(p for p in people if p["role"] == "Professor")

    intent_templates = [
        ("query_dataset_summary",  "Dataset",       datasets),
        ("review_agent_proposal",  "AgentProposal", proposals),
        ("check_project_budget",   "PurchaseRequest", None),
        ("explain_anomaly",        "Dataset",       datasets),
        ("summarise_experiment",   "Experiment",    None),
    ]

    for i in range(1, 41):
        actor  = random.choice(researchers + [prof])
        intent, etype, pool = random.choice(intent_templates)
        entity_id = random.choice(pool)[list(pool[0].keys())[0]] if pool else "N/A"

        logs.append({
            "prompt_id": make_id("PROMPT", i),
            "session_id": str(uuid4()),
            "actor_person_id": actor["person_id"],
            "actor_role": actor["security_role"],
            "intent_class": intent,
            "target_entity_type": etype,
            "target_entity_id": entity_id,
            "prompt_text": f"[synthetic prompt — intent: {intent}, entity: {entity_id}]",
            "safety_check_result": "passed",
            "timestamp": (datetime(2026, 5, random.randint(1, 31),
                                   random.randint(8, 20),
                                   random.randint(0, 59))).isoformat(),
        })

    return logs


# ── E. v0.2 Raw File Manifest ─────────────────────────────────────────────────

def generate_raw_file_manifest(people, purchases, invoices, experiments, models):
    """Metadata for raw source files: invoice PDFs, budget Excel, logs, notes."""
    rows  = []
    admin = next(p for p in people if p["role"] == "Admin")
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    fid   = 1

    # Invoice PDFs
    for inv in invoices:
        rows.append({
            "file_id":              make_id("FILE", fid),
            "file_name":            inv["source_file"],
            "file_type":            "pdf",
            "source_module":        "invoice_ocr",
            "linked_entity_type":   "Invoice",
            "linked_entity_id":     inv["invoice_id"],
            "extraction_confidence":inv["confidence"],
            "contains_error":       str(inv["project_id"] == "" or inv["purchase_request_id"] == ""),
            "uploaded_by":          admin["person_id"],
            "uploaded_at":          inv["issue_date"] + "T10:00:00",
            "storage_path":         f"minio://synthetic-dais/raw/invoices/{inv['source_file']}",
        })
        fid += 1

    # Budget Excel (one per purchase, first 20)
    for pr in purchases[:20]:
        rows.append({
            "file_id":              make_id("FILE", fid),
            "file_name":            f"budget_tracker_{pr['project_id']}_{fid:02d}.xlsx",
            "file_type":            "xlsx",
            "source_module":        "budget_tracker",
            "linked_entity_type":   "PurchaseRequest",
            "linked_entity_id":     pr["purchase_request_id"],
            "extraction_confidence":round(random.uniform(0.75, 0.98), 2),
            "contains_error":       str(pr["budget_check_status"] == "over_budget"),
            "uploaded_by":          admin["person_id"],
            "uploaded_at":          pr["created_at"],
            "storage_path":         f"minio://synthetic-dais/raw/budgets/budget_{pr['purchase_request_id']}.xlsx",
        })
        fid += 1

    # Experiment logs (first 40)
    for exp in experiments[:40]:
        rows.append({
            "file_id":              make_id("FILE", fid),
            "file_name":            f"exp_log_{exp['experiment_id']}.log",
            "file_type":            "log",
            "source_module":        "experiment_runner",
            "linked_entity_type":   "Experiment",
            "linked_entity_id":     exp["experiment_id"],
            "extraction_confidence":round(random.uniform(0.80, 0.99), 2),
            "contains_error":       str(exp["status"] == "failed"),
            "uploaded_by":          exp["researcher_person_id"],
            "uploaded_at":          exp.get("started_at") or "2026-03-01T08:00:00",
            "storage_path":         f"minio://synthetic-dais/raw/experiment_logs/{exp['experiment_id']}.log",
        })
        fid += 1

    # Model training logs (first 20)
    for mdl in models[:20]:
        rows.append({
            "file_id":              make_id("FILE", fid),
            "file_name":            f"train_log_{mdl['model_id']}.jsonl",
            "file_type":            "jsonl",
            "source_module":        "model_trainer",
            "linked_entity_type":   "ModelAsset",
            "linked_entity_id":     mdl["model_id"],
            "extraction_confidence":round(random.uniform(0.85, 0.99), 2),
            "contains_error":       str(mdl["dataset_version_status"] == "outdated"),
            "uploaded_by":          random.choice(researchers)["person_id"],
            "uploaded_at":          "2026-04-15T10:00:00",
            "storage_path":         f"minio://synthetic-dais/raw/training_logs/{mdl['model_id']}.jsonl",
        })
        fid += 1

    # Meeting notes (10)
    for i in range(1, 11):
        mo = random.randint(3, 5)
        day = random.randint(1, 28)
        rows.append({
            "file_id":              make_id("FILE", fid),
            "file_name":            f"meeting_note_2026_{i:02d}.md",
            "file_type":            "md",
            "source_module":        "meeting_notes",
            "linked_entity_type":   "Project",
            "linked_entity_id":     make_id("PJ", random.randint(1, 8)),
            "extraction_confidence":round(random.uniform(0.60, 0.90), 2),
            "contains_error":       "False",
            "uploaded_by":          admin["person_id"],
            "uploaded_at":          f"2026-{mo:02d}-{day:02d}T15:00:00",
            "storage_path":         f"minio://synthetic-dais/raw/meeting_notes/meeting_note_2026_{i:02d}.md",
        })
        fid += 1

    return rows


# ── F. v0.2 DAIS Operational Modules ─────────────────────────────────────────

def generate_lectures(people):
    """Synthetic lecture schedule based on DAIS Lab's known course portfolio."""
    courses = [
        ("Machine Learning",              "graduate"),
        ("Data Mining",                   "graduate"),
        ("Industrial AI",                 "graduate"),
        ("Artificial Intelligence",       "undergraduate"),
        ("Big Data Analysis",             "undergraduate"),
        ("Deep Learning for Engineers",   "graduate"),
        ("Digital Twin Fundamentals",     "graduate"),
        ("Pattern Recognition",           "undergraduate"),
    ]
    prof = next(p for p in people if p["role"] == "Professor")
    rows = []
    for i, (course, level) in enumerate(courses, start=1):
        rows.append({
            "lecture_id":            make_id("LEC", i),
            "course_name":           course,
            "instructor_person_id":  prof["person_id"],
            "semester":              random.choice(["Spring 2026", "Fall 2026"]),
            "year":                  2026,
            "lecture_type":          level,
            "enrolled_count":        random.randint(10, 45),
            "credits":               3,
            "language":              "Korean" if random.random() < 0.7 else "English",
        })
    return rows


def generate_off_campus_talks(people):
    """Invited talks and conference appearances for the lab PI."""
    venues = [
        ("KIIE Annual Conference, Seoul",              "Korea"),
        ("IEEE IEEM 2026, Macau",                      "International"),
        ("KSME Industrial AI Workshop, Busan",         "Korea"),
        ("Samsung SDI R&D Forum, Ulsan",               "Korea"),
        ("POSCO Digital Transformation Summit, Pohang","Korea"),
        ("Hyundai Heavy Industries AI Day, Ulsan",     "Korea"),
        ("KSC 2026, Jeju",                             "Korea"),
        ("AI Convergence Forum, Daejeon",              "Korea"),
    ]
    prof = next(p for p in people if p["role"] == "Professor")
    rows = []
    for i, (venue, country) in enumerate(venues, start=1):
        rows.append({
            "talk_id":          make_id("TALK", i),
            "speaker_person_id":prof["person_id"],
            "title":            f"Synthetic Talk {i:02d}: Industrial AI and Digital Twins for Smart Manufacturing",
            "venue":            venue,
            "date":             random_date(date(2026, 3, 1), date(2026, 12, 31)).isoformat(),
            "type":             random.choice(["invited_talk", "panel", "seminar", "keynote"]),
            "country":          country,
        })
    return rows


def generate_recruiting_pipeline(people):
    """Lab student recruitment pipeline (MS / PhD / OpenLab)."""
    interests = [
        "Industrial AI", "Anomaly Detection", "Digital Twin",
        "Machine Vision", "Time-series Analytics", "Manufacturing AI", "Causal ML",
    ]
    institutions = ["UNIST", "POSTECH", "KAIST", "Ulsan University", "Pusan National University"]
    rows = []
    for i in range(1, 21):
        pos = random.choice(["MS", "PhD", "OpenLab"])
        rows.append({
            "candidate_id":             make_id("CAND", i),
            "display_name":             f"Candidate_{i:03d}",
            "applying_for":             pos,
            "research_interest":        random.choice(interests),
            "application_date":         random_date(date(2026, 2, 1), date(2026, 5, 31)).isoformat(),
            "status":                   random.choice(["applied", "screening", "interview", "offered", "rejected", "accepted"]),
            "interviewer_person_id":    "P-0001",
            "gpa":                      round(random.uniform(3.0, 4.5), 2),
            "undergraduate_institution":random.choice(institutions),
        })
    return rows


def generate_openlab_activities(people, projects):
    """OpenLab undergraduate activity log."""
    interns = [p for p in people if p["role"] == "UndergraduateOpenLab"]
    activity_types = [
        "Data labeling", "Literature review", "Prototype build",
        "Dataset collection", "Experiment support", "Paper review",
        "ML tutorial", "Hardware setup",
    ]
    rows = []
    for i in range(1, 31):
        person  = random.choice(interns)
        project = random.choice(projects)
        rows.append({
            "activity_id":       make_id("OL", i),
            "person_id":         person["person_id"],
            "activity_type":     random.choice(activity_types),
            "project_id":        project["project_id"],
            "description":       f"Synthetic OpenLab activity {i:03d} for {project['theme']}",
            "date":              random_date(date(2026, 3, 1), date(2026, 8, 31)).isoformat(),
            "mentor_person_id":  "P-0001",
            "hours_logged":      random.randint(2, 40),
            "outcome":           random.choice(["completed", "in_progress", "cancelled"]),
        })
    return rows


def generate_achievements(people):
    """Lab awards, best papers, and scholarships."""
    achievement_types = [
        "Best Paper Award", "Outstanding Reviewer", "Research Excellence Award",
        "NRF Fellowship", "Industry Collaboration Award", "Top Poster Award",
    ]
    venues = ["KIIE 2025", "IEEE IEEM 2025", "KSME 2026", "NRF Grant Panel 2026"]
    eligible = [p for p in people if p["security_role"] in ["Researcher", "Professor"]]
    rows = []
    for i in range(1, 16):
        person = random.choice(eligible)
        rows.append({
            "achievement_id":    make_id("ACH", i),
            "person_id":         person["person_id"],
            "achievement_type":  random.choice(achievement_types),
            "title":             f"Synthetic Achievement {i:02d}",
            "date":              random_date(date(2025, 1, 1), date(2026, 6, 1)).isoformat(),
            "venue":             random.choice(venues),
            "monetary_value_krw":random.choice([0, 0, 500_000, 1_000_000, 5_000_000]),
        })
    return rows


def generate_student_skills(people):
    """Researcher skill profiles."""
    all_skills = [
        "Python", "PyTorch", "TensorFlow", "Scikit-learn", "PySpark",
        "MATLAB", "C++", "ROS", "Docker", "Kubernetes",
        "SQL", "Apache Kafka", "MLflow", "Grafana", "SHAP",
        "Time-series Analysis", "Computer Vision", "NLP", "Causal Inference", "Digital Twin",
        "Industrial IoT", "SPARQL", "OWL/RDF", "Process Mining", "Anomaly Detection",
    ]
    eligible = [p for p in people if p["security_role"] in ["Researcher", "Guest"]]
    rows = []
    idx = 1
    for person in eligible:
        for skill in random.sample(all_skills, random.randint(3, 8)):
            rows.append({
                "skill_id":         make_id("SKL", idx),
                "person_id":        person["person_id"],
                "skill_name":       skill,
                "proficiency_level":random.choice(["beginner", "intermediate", "advanced", "expert"]),
                "certified":        random.choice(["True", "False", "False"]),
                "last_used_date":   random_date(date(2025, 6, 1), date(2026, 6, 1)).isoformat(),
            })
            idx += 1
    return rows


# ── G. v0.2 Domain-Specific Project Data ─────────────────────────────────────

def generate_bess_sensor_logs(projects, equipment):
    """Thermal / gas sensor telemetry for the BESS safety project."""
    bess = next((p for p in projects if "BESS" in p["project_code"]), None)
    if not bess:
        return []

    bess_eq = [e for e in equipment if e["category"] in ["Sensor Kit", "Edge AI Device"]] or equipment
    rows = []
    for i in range(1, 121):
        eq   = random.choice(bess_eq)
        temp = round(random.uniform(18.0, 85.0), 1)
        gas  = round(random.uniform(0.0, 450.0), 1)
        fire = temp > 65.0 or gas > 300.0
        rows.append({
            "log_id":                make_id("BESS", i),
            "project_id":            bess["project_id"],
            "equipment_id":          eq["equipment_id"],
            "timestamp":             (datetime(2026, 4, 1) + timedelta(hours=i * 2)).isoformat(),
            "cell_voltage_v":        round(random.uniform(3.0, 4.2), 3),
            "temperature_c":         temp,
            "gas_concentration_ppm": gas,
            "fire_risk_flag":        str(fire),
            "anomaly_flag":          str(fire or random.random() < 0.05),
            "sensor_id":             f"BESS-SENSOR-{random.randint(1, 8):02d}",
        })
    return rows


def generate_welding_images(projects, experiments, models):
    """Radiographic image metadata for the welding NDT project."""
    weld = next((p for p in projects if "WELD" in p["project_code"]), None)
    if not weld:
        return []

    defect_types = ["porosity", "crack", "slag_inclusion", "undercut", "incomplete_fusion", "no_defect"]
    nf_models    = [m for m in models if m["model_type"] == "NormalizingFlow"
                    and m["project_id"] == weld["project_id"]] or models
    weld_exps    = [e["experiment_id"] for e in experiments if e["project_id"] == weld["project_id"]] \
                   or [experiments[0]["experiment_id"]]

    rows = []
    for i in range(1, 81):
        defect = random.choice(defect_types)
        rows.append({
            "image_id":               make_id("WELD", i),
            "project_id":             weld["project_id"],
            "experiment_id":          random.choice(weld_exps),
            "filename":               f"weld_xray_{i:04d}.png",
            "defect_type":            defect,
            "defect_label":           "defective" if defect != "no_defect" else "ok",
            "model_id":               random.choice(nf_models)["model_id"],
            "prediction_confidence":  round(random.uniform(0.65, 0.99), 3),
            "radiographic_thickness_mm": round(random.uniform(5.0, 40.0), 1),
            "inspection_date":        random_date(date(2026, 3, 1), date(2026, 8, 31)).isoformat(),
        })
    return rows


def generate_hydraulic_sensor_logs(projects, equipment):
    """Pressure / flow sensor logs for the hydraulic quality monitoring project."""
    hyd = next((p for p in projects if "HYD" in p["project_code"]), None)
    if not hyd:
        return []

    hyd_eq = [e for e in equipment if e["category"] in ["Sensor Kit", "Inspection Rig"]] or equipment
    rows   = []
    for i in range(1, 101):
        eq       = random.choice(hyd_eq)
        pressure = round(random.uniform(80.0, 320.0), 1)
        flow     = round(random.uniform(5.0, 80.0), 2)
        anomaly  = pressure > 280.0 or flow < 8.0
        rows.append({
            "log_id":              make_id("HYD", i),
            "project_id":          hyd["project_id"],
            "equipment_id":        eq["equipment_id"],
            "timestamp":           (datetime(2026, 4, 1) + timedelta(hours=i)).isoformat(),
            "pressure_bar":        pressure,
            "flow_rate_lpm":       flow,
            "cylinder_stroke_mm":  round(random.uniform(50.0, 500.0), 1),
            "quality_label":       "fail" if anomaly else "pass",
            "anomaly_flag":        str(anomaly),
        })
    return rows


def generate_semiconductor_sim_runs(projects, models):
    """Simulation runs for the semiconductor digital twin project."""
    semi = next((p for p in projects if "SEMI" in p["project_code"]), None)
    if not semi:
        return []

    semi_models = [m for m in models if m["project_id"] == semi["project_id"]] or models
    rows = []
    for i in range(1, 61):
        mdl = random.choice(semi_models)
        rows.append({
            "run_id":               make_id("SEMI", i),
            "project_id":           semi["project_id"],
            "model_id":             mdl["model_id"],
            "simulation_config":    json.dumps({
                "temperature_c":    round(random.uniform(150, 450), 1),
                "pressure_mbar":    round(random.uniform(1.0, 10.0), 2),
                "gas_flow_sccm":    round(random.uniform(50, 500), 1),
            }),
            "yield_percent":        round(random.uniform(75.0, 99.5), 2),
            "cycle_time_sec":       random.randint(30, 300),
            "defect_density_per_cm2": round(random.uniform(0.01, 5.0), 3),
            "status":               "completed" if random.random() > 0.05 else "failed",
            "run_date":             random_date(date(2026, 3, 1), date(2026, 8, 31)).isoformat(),
        })
    return rows


def generate_port_event_logs(projects):
    """Process-mining event log for the port digital transformation project."""
    port = next((p for p in projects if "PORT" in p["project_code"]), None)
    if not port:
        return []

    operations = [
        "vessel_arrival", "berth_assignment", "crane_start", "crane_end",
        "container_unload", "customs_clearance", "container_load", "vessel_departure",
    ]
    rows = []
    for i in range(1, 121):
        op       = random.choice(operations)
        start    = datetime(2026, 4, random.randint(1, 30),
                            random.randint(0, 23), random.randint(0, 59))
        duration = random.randint(10, 480)
        end      = start + timedelta(minutes=duration)
        bottleneck = duration > 300 or (op == "customs_clearance" and duration > 120)
        rows.append({
            "event_id":       make_id("PORT", i),
            "project_id":     port["project_id"],
            "vessel_id":      f"VESSEL-{random.randint(1, 20):03d}",
            "operation_type": op,
            "start_time":     start.isoformat(),
            "end_time":       end.isoformat(),
            "duration_min":   duration,
            "bottleneck_flag":str(bottleneck),
            "case_id":        f"CASE-{random.randint(1, 30):03d}",
        })
    return rows


def generate_anomaly_records(projects, datasets, models, experiments):
    """Multivariate time-series anomaly records for the system anomaly detection project."""
    anom = next((p for p in projects if "ANOM" in p["project_code"]), None)
    if not anom:
        return []

    anomaly_types = [
        "point_anomaly", "contextual_anomaly", "collective_anomaly",
        "trend_shift", "level_shift", "seasonal_deviation",
    ]
    detectors = ["LSTM_model", "IsolationForest", "NormalizingFlow", "threshold_rule"]

    ad  = [d for d in datasets  if d["project_id"] == anom["project_id"]] or datasets
    am  = [m for m in models    if m["project_id"] == anom["project_id"]] or models
    ae  = [e for e in experiments if e["project_id"] == anom["project_id"]] or experiments

    rows = []
    for i in range(1, 81):
        rows.append({
            "anomaly_id":    make_id("ANOM", i),
            "project_id":    anom["project_id"],
            "dataset_id":    random.choice(ad)["dataset_id"],
            "model_id":      random.choice(am)["model_id"],
            "experiment_id": random.choice(ae)["experiment_id"],
            "timestamp":     (datetime(2026, 4, 1) + timedelta(hours=random.randint(0, 2000))).isoformat(),
            "anomaly_type":  random.choice(anomaly_types),
            "severity":      random.choice(["low", "medium", "medium", "high"]),
            "anomaly_score": round(random.uniform(0.50, 0.99), 3),
            "detected_by":   random.choice(detectors),
            "confirmed":     str(random.random() < 0.70),
            "resolution":    random.choice(["acknowledged", "false_positive", "root_cause_found", "pending"]),
        })
    return rows


# ── H. v0.2 Reports ───────────────────────────────────────────────────────────

def build_data_quality_report(datasets, models, purchases, invoices,
                               publications, experiments, equipment_reservations):
    anomalies = []

    for d in datasets:
        if not d["owner_person_id"]:
            anomalies.append({"type": "MISSING_DATASET_OWNER",        "entity": "Dataset",            "id": d["dataset_id"],  "severity": "medium"})

    for m in models:
        if m["dataset_version_status"] == "outdated":
            anomalies.append({"type": "OUTDATED_DATASET_VERSION",     "entity": "ModelAsset",         "id": m["model_id"],    "severity": "high"})

    for pr in purchases:
        if pr["budget_check_status"] == "over_budget":
            anomalies.append({"type": "OVER_BUDGET_PURCHASE",         "entity": "PurchaseRequest",    "id": pr["purchase_request_id"], "severity": "high"})

    for inv in invoices:
        if not inv["project_id"]:
            anomalies.append({"type": "UNLINKED_INVOICE_NO_PROJECT",  "entity": "Invoice",            "id": inv["invoice_id"],"severity": "medium"})
        if not inv["purchase_request_id"]:
            anomalies.append({"type": "UNLINKED_INVOICE_NO_PR",       "entity": "Invoice",            "id": inv["invoice_id"],"severity": "medium"})

    for pub in publications:
        if pub["reproducibility_package_status"] == "incomplete":
            anomalies.append({"type": "INCOMPLETE_PUB_LINEAGE",       "entity": "Publication",        "id": pub["publication_id"], "severity": "medium"})

    conflict_ids = {"RSV-0901", "RSV-0902"}
    for r in equipment_reservations:
        if r["reservation_id"] in conflict_ids:
            anomalies.append({"type": "EQUIPMENT_DOUBLE_BOOKING",     "entity": "EquipmentReservation","id": r["reservation_id"], "severity": "high"})

    by_type     = {}
    by_severity = {"low": 0, "medium": 0, "high": 0}
    for a in anomalies:
        by_type[a["type"]]         = by_type.get(a["type"], 0) + 1
        by_severity[a["severity"]] = by_severity.get(a["severity"], 0) + 1

    return {
        "generated_at": utcnow_str(),
        "version": "v0.2",
        "total_anomalies": len(anomalies),
        "by_type": by_type,
        "by_severity": by_severity,
        "anomalies": anomalies,
    }


# ── I. Main ───────────────────────────────────────────────────────────────────

def main():
    # ── v0.1 entities ──────────────────────────────────────────────────────
    people              = generate_people()
    projects            = generate_projects()
    project_members     = generate_project_members(people, projects)
    equipment           = generate_equipment()
    datasets            = generate_datasets(projects, people)
    models              = generate_models(projects, datasets)
    experiments         = generate_experiments(projects, datasets, models, equipment, people)
    equipment_reservations = generate_equipment_reservations(equipment, experiments)
    purchases           = generate_purchases(projects, people)
    invoices            = generate_invoices(projects, purchases)
    milestones          = generate_milestones(projects)
    publications        = generate_publications(projects, datasets, models, experiments)
    events              = generate_events(projects, datasets, models, experiments, purchases, invoices)
    proposals           = generate_agent_proposals(
        datasets=datasets, models=models,
        equipment_reservations=equipment_reservations,
        purchases=purchases, invoices=invoices, publications=publications,
    )

    # ── v0.2 entities ──────────────────────────────────────────────────────
    workflow_events     = generate_workflow_events(
        people, projects, datasets, models, experiments, purchases, invoices, proposals)
    role_permissions    = generate_role_permissions()
    access_attempts     = generate_access_attempts(people, datasets)
    approval_records    = generate_approval_records(people, purchases, datasets, proposals)
    audit_logs          = generate_audit_logs(people, access_attempts, approval_records, datasets)
    security_events     = generate_security_events(people, access_attempts, proposals)
    prompt_history      = generate_prompt_history(people, proposals, datasets)
    raw_file_manifest   = generate_raw_file_manifest(people, purchases, invoices, experiments, models)
    lectures            = generate_lectures(people)
    off_campus_talks    = generate_off_campus_talks(people)
    recruiting_pipeline = generate_recruiting_pipeline(people)
    openlab_activities  = generate_openlab_activities(people, projects)
    achievements        = generate_achievements(people)
    student_skills      = generate_student_skills(people)
    bess_logs           = generate_bess_sensor_logs(projects, equipment)
    welding_images      = generate_welding_images(projects, experiments, models)
    hydraulic_logs      = generate_hydraulic_sensor_logs(projects, equipment)
    semi_runs           = generate_semiconductor_sim_runs(projects, models)
    port_logs           = generate_port_event_logs(projects)
    anomaly_records     = generate_anomaly_records(projects, datasets, models, experiments)

    # ── Write v0.1 CSVs (schema-compatible, temporal-fixed experiments) ────
    write_csv("people.csv",                 people)
    write_csv("projects.csv",               projects)
    write_csv("project_members.csv",        project_members)
    write_csv("equipment.csv",              equipment)
    write_csv("datasets.csv",               datasets)
    write_csv("model_assets.csv",           models)
    write_csv("experiments.csv",            experiments)
    write_csv("equipment_reservations.csv", equipment_reservations)
    write_csv("purchase_requests.csv",      purchases)
    write_csv("invoices.csv",               invoices)
    write_csv("milestones.csv",             milestones)
    write_csv("publications.csv",           publications)
    write_jsonl("erp_events.jsonl",         events)
    write_json("agent_proposals.json",      proposals)

    # ── Write v0.2 files ───────────────────────────────────────────────────
    write_jsonl("workflow_events.jsonl",        workflow_events)
    write_csv("role_permissions.csv",           role_permissions)
    write_csv("access_attempts.csv",            access_attempts)
    write_csv("approval_records.csv",           approval_records)
    write_jsonl("audit_logs.jsonl",             audit_logs)
    write_csv("security_events.csv",            security_events)
    write_jsonl("prompt_history.jsonl",         prompt_history)
    write_csv("raw_file_manifest.csv",          raw_file_manifest)
    write_csv("lectures.csv",                   lectures)
    write_csv("off_campus_talks.csv",           off_campus_talks)
    write_csv("recruiting_pipeline.csv",        recruiting_pipeline)
    write_csv("openlab_activities.csv",         openlab_activities)
    write_csv("achievements.csv",               achievements)
    write_csv("student_skills.csv",             student_skills)
    write_csv("bess_sensor_logs.csv",           bess_logs)
    write_csv("welding_images.csv",             welding_images)
    write_csv("hydraulic_sensor_logs.csv",      hydraulic_logs)
    write_csv("semiconductor_sim_runs.csv",     semi_runs)
    write_csv("port_event_logs.csv",            port_logs)
    write_csv("anomaly_records.csv",            anomaly_records)

    # ── Reports ────────────────────────────────────────────────────────────
    dq_report = build_data_quality_report(
        datasets, models, purchases, invoices,
        publications, experiments, equipment_reservations)
    write_json("data_quality_report_v02.json", dq_report)

    summary = {
        "version": "v0.2",
        "generated_at": utcnow_str(),
        "v01_entities": {
            "people":                   len(people),
            "projects":                 len(projects),
            "project_members":          len(project_members),
            "equipment":                len(equipment),
            "datasets":                 len(datasets),
            "model_assets":             len(models),
            "experiments":              len(experiments),
            "equipment_reservations":   len(equipment_reservations),
            "purchase_requests":        len(purchases),
            "invoices":                 len(invoices),
            "milestones":               len(milestones),
            "publications":             len(publications),
            "erp_events":               len(events),
            "agent_proposals":          len(proposals),
        },
        "v02_entities": {
            "workflow_events":          len(workflow_events),
            "role_permissions":         len(role_permissions),
            "access_attempts":          len(access_attempts),
            "approval_records":         len(approval_records),
            "audit_logs":               len(audit_logs),
            "security_events":          len(security_events),
            "prompt_history":           len(prompt_history),
            "raw_file_manifest":        len(raw_file_manifest),
            "lectures":                 len(lectures),
            "off_campus_talks":         len(off_campus_talks),
            "recruiting_pipeline":      len(recruiting_pipeline),
            "openlab_activities":       len(openlab_activities),
            "achievements":             len(achievements),
            "student_skills":           len(student_skills),
            "bess_sensor_logs":         len(bess_logs),
            "welding_images":           len(welding_images),
            "hydraulic_sensor_logs":    len(hydraulic_logs),
            "semiconductor_sim_runs":   len(semi_runs),
            "port_event_logs":          len(port_logs),
            "anomaly_records":          len(anomaly_records),
        },
        "injected_anomalies": dq_report["by_type"],
        "anomaly_severity_breakdown": dq_report["by_severity"],
        "total_anomalies": dq_report["total_anomalies"],
        "total_output_files": 34,
    }
    write_json("generation_summary_v02.json", summary)

    # ── Print ──────────────────────────────────────────────────────────────
    print("=" * 60)
    print("  DAIS ERP Twin — Synthetic Data Generator v0.2")
    print("=" * 60)
    print("\n── v0.1 entities (temporal-fixed) ──")
    for k, v in summary["v01_entities"].items():
        print(f"  {k:<30} {v:>5}")
    print("\n── v0.2 entities ──")
    for k, v in summary["v02_entities"].items():
        print(f"  {k:<30} {v:>5}")
    print("\n── Injected anomalies ──")
    for k, v in summary["injected_anomalies"].items():
        print(f"  {k:<40} {v:>3}")
    print(f"\n  Total anomalies : {dq_report['total_anomalies']}")
    print(f"  Severity high   : {dq_report['by_severity']['high']}")
    print(f"  Severity medium : {dq_report['by_severity']['medium']}")
    print(f"  Output dir      : {OUT_DIR.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()

import csv
import json
import random
import hashlib
from uuid import uuid4
from pathlib import Path
from datetime import datetime, timedelta, date

random.seed(42)

OUT_DIR = Path("synthetic_data/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def make_id(prefix: str, n: int) -> str:
    return f"{prefix}-{n:04d}"


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


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
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(filename: str, data):
    path = OUT_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
        ("SYN-PJ-2026-BESS-SAFE", "Battery Energy Storage System Safety Analytics", "BESS safety AI"),
        ("SYN-PJ-2026-HYD-QM", "Hydraulic Cylinder Quality Monitoring", "Hydraulic quality monitoring"),
        ("SYN-PJ-2026-WELD-NDT", "Welding Defect Detection and NDT Intelligence", "Welding inspection AI"),
        ("SYN-PJ-2026-ROBOT-CPS", "CPS-Based Autonomous Robot Monitoring", "Cyber-physical systems"),
        ("SYN-PJ-2026-SEMI-DT", "Digital Twin Simulation for Semiconductor Process Optimization", "Semiconductor digital twin"),
        ("SYN-PJ-2026-PORT-DX", "Port Process Mining and Digital Transformation", "Process mining"),
        ("SYN-PJ-2026-MV-DEFECT", "Machine Vision Defect Detection for Manufacturing", "Machine vision"),
        ("SYN-PJ-2026-SYS-ANOM", "System-Level Anomaly Detection for Industrial Operations", "System anomaly detection"),
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
    researchers = [p for p in people if p["security_role"] == "Researcher"]
    rows = []

    for i in range(1, 121):
        project = random.choice(projects)
        project_models = [m for m in models if m["project_id"] == project["project_id"]]
        model = random.choice(project_models or models)

        dataset = next((d for d in datasets if d["dataset_id"] == model["dataset_id"]), random.choice(datasets))

        missing_equipment = random.random() < 0.04
        eq = "" if missing_equipment else random.choice(equipment)["equipment_id"]

        result = {
            "loss": round(random.uniform(0.01, 0.45), 4),
            "accuracy": round(random.uniform(0.70, 0.99), 3),
            "notes": "synthetic experiment result",
        }

        rows.append({
            "experiment_id": make_id("EXP", i),
            "experiment_code": f"EXP-2026-{i:04d}",
            "project_id": project["project_id"],
            "dataset_id": dataset["dataset_id"],
            "model_id": model["model_id"],
            "equipment_id": eq,
            "researcher_person_id": random.choice(researchers)["person_id"],
            "status": random.choice(["completed", "completed", "running", "failed", "pending"]),
            "started_at": (datetime(2026, 3, 1) + timedelta(days=random.randint(0, 180))).isoformat(),
            "completed_at": (datetime(2026, 3, 1) + timedelta(days=random.randint(181, 240))).isoformat(),
            "result_json": json.dumps(result),
            "reproducibility_score": round(random.uniform(0.45, 0.98), 2),
        })

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

    # Intentional double-booking conflict
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
            "target_venue": random.choice(["Synthetic Journal of Industrial AI", "Synthetic KIIE Conference", "Synthetic IEEE Venue"]),
            "year": random.choice([2026, 2027]),
            "reproducibility_package_status": "incomplete" if missing_lineage else random.choice(["complete", "complete", "pending"]),
        })

    return rows


def create_event(event_type, entity_type, entity_id, payload, previous_hash):
    raw = json.dumps({
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": payload,
        "previous_hash": previous_hash,
    }, sort_keys=True)

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
        "created_at": datetime.utcnow().isoformat(),
    }


def generate_events(projects, datasets, models, experiments, purchases, invoices):
    events = []
    prev = "GENESIS"

    event_inputs = []

    for p in projects:
        event_inputs.append(("ProjectCreated", "Project", p["project_id"], p))

    for d in datasets:
        event_inputs.append(("DatasetRegistered", "Dataset", d["dataset_id"], d))

    for m in models:
        event_inputs.append(("ModelRegistered", "ModelAsset", m["model_id"], m))

    for e in experiments:
        event_inputs.append(("ExperimentRecorded", "Experiment", e["experiment_id"], e))

    for pr in purchases:
        event_inputs.append(("PurchaseRequested", "PurchaseRequest", pr["purchase_request_id"], pr))

    for inv in invoices:
        event_inputs.append(("InvoiceReceived", "Invoice", inv["invoice_id"], inv))

    for event_type, entity_type, entity_id, payload in event_inputs:
        ev = create_event(event_type, entity_type, entity_id, payload, prev)
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
            "created_at": datetime.utcnow().isoformat(),
            "requires_approval": True,
        })

    for inv in invoices:
        if inv["project_id"] == "":
            add(
                "LINK_INVOICE_TO_PROJECT",
                f"Invoice {inv['invoice_code']} has no linked project",
                "Invoice",
                inv["invoice_id"],
                "medium",
                inv["confidence"],
                ["project_id is empty", inv["source_file"], f"supplier={inv['supplier_name']}"],
            )

    for ds in datasets:
        if ds["owner_person_id"] == "":
            add(
                "ASSIGN_DATASET_OWNER",
                f"Dataset {ds['dataset_code']} has no owner",
                "Dataset",
                ds["dataset_id"],
                "medium",
                0.91,
                ["owner_person_id is empty", f"project_id={ds['project_id']}"],
            )

    for model in models:
        if model["dataset_version_status"] == "outdated":
            add(
                "REVIEW_MODEL_DATASET_VERSION",
                f"Model {model['model_code']} uses an outdated dataset version",
                "ModelAsset",
                model["model_id"],
                "high",
                0.88,
                ["dataset_version_status=outdated", f"dataset_id={model['dataset_id']}"],
            )

    for pr in purchases:
        if pr["budget_check_status"] == "over_budget":
            add(
                "REVIEW_OVER_BUDGET_PURCHASE",
                f"Purchase request {pr['request_code']} exceeds project budget",
                "PurchaseRequest",
                pr["purchase_request_id"],
                "high",
                0.95,
                ["budget_check_status=over_budget", f"amount_krw={pr['amount_krw']}"],
            )

    for pub in publications:
        if pub["reproducibility_package_status"] == "incomplete":
            add(
                "FIX_PUBLICATION_LINEAGE",
                f"Publication {pub['publication_id']} has incomplete reproducibility lineage",
                "Publication",
                pub["publication_id"],
                "medium",
                0.83,
                ["missing dataset/model/experiment link", f"project_id={pub['project_id']}"],
            )

    # Detect the intentional double booking simply by known reservation IDs
    conflict_ids = {"RSV-0901", "RSV-0902"}
    for r in equipment_reservations:
        if r["reservation_id"] in conflict_ids:
            add(
                "RESOLVE_EQUIPMENT_CONFLICT",
                f"Equipment conflict detected for reservation {r['reservation_id']}",
                "EquipmentReservation",
                r["reservation_id"],
                "high",
                0.96,
                [
                    f"equipment_id={r['equipment_id']}",
                    f"start_time={r['start_time']}",
                    f"end_time={r['end_time']}",
                ],
            )

    return proposals


def main():
    people = generate_people()
    projects = generate_projects()
    project_members = generate_project_members(people, projects)
    equipment = generate_equipment()
    datasets = generate_datasets(projects, people)
    models = generate_models(projects, datasets)
    experiments = generate_experiments(projects, datasets, models, equipment, people)
    equipment_reservations = generate_equipment_reservations(equipment, experiments)
    purchases = generate_purchases(projects, people)
    invoices = generate_invoices(projects, purchases)
    milestones = generate_milestones(projects)
    publications = generate_publications(projects, datasets, models, experiments)

    events = generate_events(projects, datasets, models, experiments, purchases, invoices)
    proposals = generate_agent_proposals(
        datasets=datasets,
        models=models,
        equipment_reservations=equipment_reservations,
        purchases=purchases,
        invoices=invoices,
        publications=publications,
    )

    write_csv("people.csv", people)
    write_csv("projects.csv", projects)
    write_csv("project_members.csv", project_members)
    write_csv("equipment.csv", equipment)
    write_csv("datasets.csv", datasets)
    write_csv("model_assets.csv", models)
    write_csv("experiments.csv", experiments)
    write_csv("equipment_reservations.csv", equipment_reservations)
    write_csv("purchase_requests.csv", purchases)
    write_csv("invoices.csv", invoices)
    write_csv("milestones.csv", milestones)
    write_csv("publications.csv", publications)

    write_jsonl("erp_events.jsonl", events)
    write_json("agent_proposals.json", proposals)

    summary = {
        "people": len(people),
        "projects": len(projects),
        "project_members": len(project_members),
        "equipment": len(equipment),
        "datasets": len(datasets),
        "model_assets": len(models),
        "experiments": len(experiments),
        "equipment_reservations": len(equipment_reservations),
        "purchase_requests": len(purchases),
        "invoices": len(invoices),
        "milestones": len(milestones),
        "publications": len(publications),
        "erp_events": len(events),
        "agent_proposals": len(proposals),
    }

    write_json("generation_summary.json", summary)

    print("Synthetic DAIS ERP data generated successfully.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

# DAIS ERP Twin — Progress Report

**Date:** 2026-06-02  
**Project:** `dais-erp-twin`  
**Status:** Synthetic data layer complete; infrastructure scaffolded

---

## 1. Project Overview

`dais-erp-twin` is a digital-twin ERP simulation system modelled on the DAIS Lab (Data-driven AI Systems Lab, University of Ulsan). The system is designed to:

- Mirror realistic lab operations (people, projects, datasets, models, experiments, publications, procurement)
- Support ERP event sourcing with a hash-chained audit log
- Enable AI agent proposals for data quality and anomaly resolution
- Serve as a test harness for ERP logic, agent workflows, and ontology validation

---

## 2. Repository Structure

```
dais-erp-twin/
├── backend/              # (scaffolded — empty)
├── docs/                 # Project documentation
│   └── progress_report.md
├── frontend/             # (scaffolded — empty)
├── ingestion/            # (scaffolded — empty)
├── ontology/             # (scaffolded — empty)
├── synthetic_data/
│   ├── generate_synthetic_dais_data.py   ← main generator
│   └── output/                           ← generated files (15 files)
├── docker/
├── docker-compose.yml
└── README.md
```

---

## 3. Completed Work

### 3.1 Synthetic Data Generator

**File:** `synthetic_data/generate_synthetic_dais_data.py`

A single-file, fully reproducible Python generator (`random.seed(42)`) that produces a relationally consistent synthetic dataset modelling DAIS lab operations.

#### Entity graph generated

```
people → projects → datasets → models → experiments
projects → purchase_requests → invoices
experiments → equipment (reservations)
models / experiments → publications
everything → ERP events (hash-chained)
problems → agent proposals
```

#### Generation summary

| Entity | Records |
|---|---|
| `people.csv` | 25 |
| `projects.csv` | 8 |
| `project_members.csv` | 44 |
| `equipment.csv` | 20 |
| `datasets.csv` | 50 |
| `model_assets.csv` | 40 |
| `experiments.csv` | 120 |
| `equipment_reservations.csv` | 62 |
| `purchase_requests.csv` | 80 |
| `invoices.csv` | 90 |
| `milestones.csv` | 40 |
| `publications.csv` | 30 |
| `erp_events.jsonl` | 388 |
| `agent_proposals.json` | 32 |

**Total output files:** 15 (12 CSV, 1 JSONL, 2 JSON)

---

### 3.2 People Model

25 synthetic lab members across four roles:

| Role | Count | Security Role |
|---|---|---|
| Professor (PI) | 1 | Professor |
| Admin | 2 | Admin |
| Graduate Researcher (MS/PhD) | 12 | Researcher |
| Undergraduate Open Lab | 10 | Researcher / Guest |

Research areas cover: Industrial AI, Causality, Digital Twin, Machine Vision, Time-series Analytics, Manufacturing AI, System Anomaly Detection, Data Mining.

---

### 3.3 Projects Model

8 projects modelled on real DAIS research themes:

| Code | Theme |
|---|---|
| `SYN-PJ-2026-BESS-SAFE` | Battery Energy Storage System Safety Analytics |
| `SYN-PJ-2026-HYD-QM` | Hydraulic Cylinder Quality Monitoring |
| `SYN-PJ-2026-WELD-NDT` | Welding Defect Detection and NDT Intelligence |
| `SYN-PJ-2026-ROBOT-CPS` | CPS-Based Autonomous Robot Monitoring |
| `SYN-PJ-2026-SEMI-DT` | Digital Twin for Semiconductor Process Optimization |
| `SYN-PJ-2026-PORT-DX` | Port Process Mining and Digital Transformation |
| `SYN-PJ-2026-MV-DEFECT` | Machine Vision Defect Detection for Manufacturing |
| `SYN-PJ-2026-SYS-ANOM` | System-Level Anomaly Detection for Industrial Operations |

Budgets range from ₩50M to ₩300M KRW. Funding agencies include synthetic NRF, MSS, KIAT, and industry partners.

---

### 3.4 ERP Event Log

388 hash-chained events in `erp_events.jsonl`. Each event carries:

- `event_id` (UUID)
- `event_type` (e.g. `ProjectCreated`, `DatasetRegistered`, `InvoiceReceived`)
- `entity_type` / `entity_id`
- `payload` (full entity snapshot)
- `previous_hash` + `event_hash` (SHA-256 chain from `GENESIS`)
- `confidence`, `created_by`, `created_at`

Event types in the chain:

| Type | Count |
|---|---|
| `ProjectCreated` | 8 |
| `DatasetRegistered` | 50 |
| `ModelRegistered` | 40 |
| `ExperimentRecorded` | 120 |
| `PurchaseRequested` | 80 |
| `InvoiceReceived` | 90 |

---

### 3.5 Intentional Data Errors (for ERP Testing)

Errors are injected with controlled probability to simulate real lab data quality issues:

| Error Type | Injection Rate | Records Affected |
|---|---|---|
| Dataset missing `owner_person_id` | ~8% | ~4 datasets |
| Model referencing outdated dataset version | ~6% | ~3 models |
| Purchase request exceeding project budget | ~5% | ~7 PRs |
| Invoice with no linked project | ~10% | ~13 invoices |
| Invoice with no linked purchase request | ~15% | ~13 invoices |
| Publication with incomplete reproducibility lineage | ~15% | ~3 publications |
| Equipment double-booking (hard-coded) | deterministic | 2 reservations |

**Double-booking detail:**  
Reservations `RSV-0901` and `RSV-0902` are both confirmed on the same equipment (`EQ-0001`) on 2026-07-15, overlapping between 12:00–14:00.

---

### 3.6 Agent Proposals

32 pending proposals in `agent_proposals.json`, surfacing all injected errors:

| Proposal Type | Count |
|---|---|
| `LINK_INVOICE_TO_PROJECT` | 13 |
| `REVIEW_OVER_BUDGET_PURCHASE` | 7 |
| `ASSIGN_DATASET_OWNER` | 4 |
| `REVIEW_MODEL_DATASET_VERSION` | 3 |
| `FIX_PUBLICATION_LINEAGE` | 3 |
| `RESOLVE_EQUIPMENT_CONFLICT` | 2 |

Each proposal includes: `proposal_type`, `title`, `affected_entity_type`, `affected_entity_id`, `risk_level`, `confidence`, `evidence[]`, `requires_approval: true`, `status: pending`.

---

## 4. Infrastructure Scaffolded (Not Yet Implemented)

| Component | Status |
|---|---|
| `backend/` | Directory created; no code yet |
| `frontend/` | Directory created; no code yet |
| `ingestion/` | Directory created; no code yet |
| `ontology/` | Directory created; no code yet |
| `docker-compose.yml` | File created; empty |
| `README.md` | File created; empty |

---

## 5. Next Steps (Suggested)

- [ ] Define ontology schema (OWL/SHACL) in `ontology/` for ERP entities
- [ ] Implement ingestion pipeline to load CSV/JSONL into a graph store or relational DB
- [ ] Build backend API (FastAPI / Spring Boot) serving ERP entities and event log
- [ ] Implement agent proposal evaluation and approval workflow
- [ ] Wire `docker-compose.yml` (Postgres / Neo4j / MinIO / API / frontend)
- [ ] Build frontend dashboard for project/experiment/purchase visibility
- [ ] Add ontology-based consistency checks against SHACL constraints
- [ ] Extend synthetic generator with time-series sensor data for experiments

---

## 6. How to Regenerate Data

```bash
cd ~/projects/dais-erp-twin
python synthetic_data/generate_synthetic_dais_data.py
```

Output is fully deterministic (`random.seed(42)`). All files are written to `synthetic_data/output/`.

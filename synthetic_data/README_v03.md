# DAIS ERP Twin — Synthetic Data Generator v0.3

Synthetic ERP dataset for **ShamsDAIS / DAIS-ERP Twin**, the secure agentic lab resource-planning system for DAIS Lab, University of Ulsan.

---

## What v0.3 Adds Over v0.2

| Feature | v0.2 | v0.3 |
|---|---|---|
| `--mode normal \| stress` CLI flag | ✗ | ✓ |
| `SYS-0001` SystemAgent in `people.csv` | ✗ | ✓ |
| `actor_type` field on every person row | ✗ | ✓ |
| Algorithmic equipment-conflict detection | hardcoded | `itertools.combinations` |
| Extended purchase statuses (7 states) | 3 states | `pending/approved/ordered/received/invoiced/paid/rejected` |
| Publications: `authors`, `doi_like_id`, `code_commit`, `artifact_path` | ✗ | ✓ |
| Models: `dataset_version`, `artifact_path`, `hyperparameters` | ✗ | ✓ |
| `now_str()` uses timezone-aware `datetime.now(timezone.utc)` | deprecation warning | ✓ |
| Quality report: temporal error check + ERP chain validation | partial | ✓ |
| Output version-isolated to `output_v03/` | `output/` | `output_v03/` |

---

## How to Run

```bash
cd /home/alrezshams/projects/dais-erp-twin

# normal mode — realistic anomaly rates (5–15 %)
python3 synthetic_data/generate_synthetic_dais_data_v03.py --mode normal

# stress mode — elevated anomaly rates (30–60 %) for robustness testing
python3 synthetic_data/generate_synthetic_dais_data_v03.py --mode stress
```

Dependencies (install once):

```bash
pip install -r requirements.txt
```

---

## Output Files (`synthetic_data/output_v03/`)

| File | Type | Rows (normal) | Description |
|---|---|---|---|
| `people.csv` | CSV | 26 | Lab members + SystemAgent (`SYS-0001`) |
| `projects.csv` | CSV | 8 | Active research projects |
| `project_members.csv` | CSV | 44 | Person ↔ project memberships |
| `equipment.csv` | CSV | 20 | Lab equipment assets |
| `equipment_reservations.csv` | CSV | 62 | Booking records |
| `datasets.csv` | CSV | 50 | Managed datasets |
| `model_assets.csv` | CSV | 40 | Trained ML models with hyperparams |
| `experiments.csv` | CSV | 120 | Experiment runs (temporally consistent) |
| `purchase_requests.csv` | CSV | 80 | Purchase requests (7-state workflow) |
| `invoices.csv` | CSV | 90 | Invoices linked to purchases |
| `milestones.csv` | CSV | 40 | Project milestones |
| `publications.csv` | CSV | 30 | Papers with DOI, commit, artifact path |
| `erp_events.jsonl` | JSONL | 388 | SHA-256 hash-chained ERP audit trail |
| `agent_proposals.json` | JSON | 29 | Agentic AI action proposals |
| `data_quality_report_v03.json` | JSON | — | Anomaly summary + chain validity |
| `generation_summary_v03.json` | JSON | — | Counts, mode, timestamps |
| `raw/` | dir | — | Reserved for raw binary/text artifacts |

---

## Injected Anomalies

Anomaly injection rates scale with `--mode`:

| Anomaly Type | normal | stress |
|---|---|---|
| Out-of-budget purchase | ~10 % | ~50 % |
| Failed access attempt | ~5 % | ~30 % |
| Rejected agent proposal | ~15 % | ~60 % |
| Equipment double-booking | detected algorithmically | same |

In **stress mode**, `agent_proposals.json` contains ~4× more entries to simulate an overloaded agentic queue.

---

## 8 Research Themes

1. BESS battery safety & fire-risk prediction  
2. Hydraulic system quality management  
3. Welding NDT & defect detection  
4. Robotic CPS & digital twin  
5. Semiconductor process digital twin  
6. Port logistics process mining  
7. Machine vision & industrial inspection  
8. Cross-domain system anomaly detection  

---

## SystemAgent (`SYS-0001`)

- Appears in `people.csv` with `actor_type = SystemAgent`
- Generates proposals in `agent_proposals.json` for automated ERP actions
- **Never self-approves** — all proposals require a human `actor_type = Person`
- Identity preserved across all future v0.3 modules

---

## Key Invariants

- `random.seed(42)` — fully deterministic output
- ID formats: `P-NNNN`, `SYS-0001`, `PJ-NNNN`, `DS-NNNN`, `MDL-NNNN`, `EXP-NNNN`, `PR-NNNN`, `INV-NNNN`, `EQ-NNNN`, `RSV-NNNN`, `AP-NNNN`, `PUB-NNNN`, `MS-NNNN`
- ERP event chain starts from `"GENESIS"` and is validated in the quality report
- v0.1 and v0.2 generators are **never modified**

---

## Roadmap (Deferred to Later v0.3 Steps)

- [ ] Raw binary artifacts: PDF invoices (reportlab), Excel budgets (openpyxl), JSON experiment logs, JSONL training logs, MD meeting notes  
- [ ] `workflow_events.jsonl` with SHA-256 hash chain  
- [ ] Realistic `prompt_history.jsonl` with injection-attempt cases  
- [ ] Full security events / audit logs module  
- [ ] Purchase-workflow status reconciliation validation (0-mismatch goal)  
- [ ] Domain improvements: BESS fire-risk score, welding NF lineage, semiconductor what-if  

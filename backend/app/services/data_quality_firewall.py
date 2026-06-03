import os
import json
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor


DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5433")),
    "dbname": os.getenv("POSTGRES_DB", "dais_erp"),
    "user": os.getenv("POSTGRES_USER", "dais"),
    "password": os.getenv("POSTGRES_PASSWORD", "dais_dev_password"),
}


def connect():
    return psycopg2.connect(**DB_CONFIG)


def fetch_count(cur, query):
    cur.execute(query)
    return cur.fetchone()["count"]


def fetch_examples(cur, query, limit=5):
    cur.execute(query, {"limit": limit})
    return [dict(row) for row in cur.fetchall()]


def make_issue(
    issue_id,
    category,
    severity,
    title,
    count,
    description,
    recommended_action,
    examples,
):
    return {
        "issue_id": issue_id,
        "category": category,
        "severity": severity,
        "title": title,
        "count": count,
        "description": description,
        "recommended_action": recommended_action,
        "examples": examples,
    }


def generate_data_quality_report():
    issues = []

    conn = connect()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Unlinked invoices
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM invoices
                WHERE project_id IS NULL;
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT invoice_id, invoice_code, supplier_name, amount_krw, issue_date, confidence
                FROM invoices
                WHERE project_id IS NULL
                ORDER BY confidence DESC NULLS LAST
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-001",
                        category="Finance / Invoice",
                        severity="medium",
                        title="Invoices without linked projects",
                        count=count,
                        description="These invoices are not linked to any project, so project-level cost tracking is incomplete.",
                        recommended_action="Create agent proposals to link each invoice to the most likely project using supplier, purchase request, date, and amount evidence.",
                        examples=examples,
                    )
                )

            # 2. Datasets without owners
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM datasets
                WHERE owner_person_id IS NULL;
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT dataset_id, dataset_code, title, project_id, sensitivity_level, quality_score
                FROM datasets
                WHERE owner_person_id IS NULL
                ORDER BY sensitivity_level DESC, quality_score ASC NULLS LAST
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-002",
                        category="Research Data",
                        severity="medium",
                        title="Datasets without owners",
                        count=count,
                        description="These datasets have no responsible owner, which creates accountability and reproducibility risk.",
                        recommended_action="Assign a dataset owner from the project team and create an approval record.",
                        examples=examples,
                    )
                )

            # 3. Outdated model dataset versions
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM model_assets
                WHERE dataset_version_status = 'outdated';
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT model_id, model_code, name, project_id, dataset_id, version, accuracy, f1_score
                FROM model_assets
                WHERE dataset_version_status = 'outdated'
                ORDER BY accuracy DESC NULLS LAST
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-003",
                        category="Model Lineage",
                        severity="high",
                        title="Models using outdated dataset versions",
                        count=count,
                        description="These models were trained or registered against outdated dataset versions, creating reproducibility and validity risk.",
                        recommended_action="Review model lineage and either retrain the model or approve the old dataset version with justification.",
                        examples=examples,
                    )
                )

            # 4. Over-budget purchase requests
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM purchase_requests
                WHERE budget_check_status = 'over_budget';
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT pr.purchase_request_id, pr.request_code, pr.project_id, p.project_code,
                       pr.item_name, pr.amount_krw, pr.status
                FROM purchase_requests pr
                LEFT JOIN projects p ON pr.project_id = p.project_id
                WHERE pr.budget_check_status = 'over_budget'
                ORDER BY pr.amount_krw DESC
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-004",
                        category="Procurement / Budget",
                        severity="high",
                        title="Over-budget purchase requests",
                        count=count,
                        description="These purchase requests exceed the project budget rule and require professor-level review.",
                        recommended_action="Block automatic approval and route these requests to Professor-level approval with budget evidence.",
                        examples=examples,
                    )
                )

            # 5. Equipment reservation conflicts
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM equipment_reservations a
                JOIN equipment_reservations b
                  ON a.equipment_id = b.equipment_id
                 AND a.reservation_id < b.reservation_id
                 AND a.status = 'confirmed'
                 AND b.status = 'confirmed'
                 AND a.start_time < b.end_time
                 AND b.start_time < a.end_time;
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT
                    a.equipment_id,
                    e.name AS equipment_name,
                    a.reservation_id AS reservation_a,
                    b.reservation_id AS reservation_b,
                    a.start_time AS a_start,
                    a.end_time AS a_end,
                    b.start_time AS b_start,
                    b.end_time AS b_end
                FROM equipment_reservations a
                JOIN equipment_reservations b
                  ON a.equipment_id = b.equipment_id
                 AND a.reservation_id < b.reservation_id
                 AND a.status = 'confirmed'
                 AND b.status = 'confirmed'
                 AND a.start_time < b.end_time
                 AND b.start_time < a.end_time
                LEFT JOIN equipment e ON a.equipment_id = e.equipment_id
                ORDER BY a.start_time
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-005",
                        category="Equipment Scheduling",
                        severity="high",
                        title="Equipment reservation conflicts",
                        count=count,
                        description="These confirmed equipment reservations overlap in time for the same asset.",
                        recommended_action="Create conflict-resolution proposals and ask an admin or professor to reschedule one reservation.",
                        examples=examples,
                    )
                )

            # 6. High-risk pending agent proposals
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM agent_proposals
                WHERE status = 'pending'
                  AND risk_level = 'high';
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT proposal_id, proposal_type, title, affected_entity_type,
                       affected_entity_id, confidence
                FROM agent_proposals
                WHERE status = 'pending'
                  AND risk_level = 'high'
                ORDER BY confidence DESC NULLS LAST
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-006",
                        category="Agent Governance",
                        severity="high",
                        title="High-risk pending agent proposals",
                        count=count,
                        description="These AI-generated proposals are high-risk and still waiting for human approval.",
                        recommended_action="Route these proposals to Professor/Admin review before any ERP state change is applied.",
                        examples=examples,
                    )
                )

            # 7. Workflow events missing hash fields
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM workflow_events
                WHERE previous_hash IS NULL
                   OR event_hash IS NULL;
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT workflow_event_id, event_type, entity_type, entity_id
                FROM workflow_events
                WHERE previous_hash IS NULL
                   OR event_hash IS NULL
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-007",
                        category="Audit / Ledger",
                        severity="critical",
                        title="Workflow events missing hash-chain fields",
                        count=count,
                        description="Some workflow events are missing tamper-evident hash fields.",
                        recommended_action="Regenerate workflow_events.jsonl or repair the event ledger before trusting audit history.",
                        examples=examples,
                    )
                )

            # 8. Publications with incomplete reproducibility package
            count = fetch_count(
                cur,
                """
                SELECT COUNT(*)
                FROM publications
                WHERE reproducibility_package_status = 'incomplete'
                   OR dataset_id IS NULL
                   OR model_id IS NULL
                   OR experiment_id IS NULL;
                """,
            )

            examples = fetch_examples(
                cur,
                """
                SELECT publication_id, title, project_id, dataset_id, model_id,
                       experiment_id, reproducibility_package_status
                FROM publications
                WHERE reproducibility_package_status = 'incomplete'
                   OR dataset_id IS NULL
                   OR model_id IS NULL
                   OR experiment_id IS NULL
                LIMIT %(limit)s;
                """,
            )

            if count > 0:
                issues.append(
                    make_issue(
                        issue_id="DQ-008",
                        category="Publication / Reproducibility",
                        severity="medium",
                        title="Publications with incomplete reproducibility lineage",
                        count=count,
                        description="These publications are missing dataset, model, experiment, or reproducibility package links.",
                        recommended_action="Link each publication to the correct dataset, model, experiment, code commit, and artifact path.",
                        examples=examples,
                    )
                )

    finally:
        conn.close()

    severity_counts = {
        "critical": sum(1 for issue in issues if issue["severity"] == "critical"),
        "high": sum(1 for issue in issues if issue["severity"] == "high"),
        "medium": sum(1 for issue in issues if issue["severity"] == "medium"),
        "low": sum(1 for issue in issues if issue["severity"] == "low"),
    }

    total_issue_instances = sum(issue["count"] for issue in issues)

    report = {
        "system": "ShamsDAIS / DAIS-ERP Twin",
        "module": "Data Quality Firewall",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": {
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "name": DB_CONFIG["dbname"],
        },
        "summary": {
            "issue_types": len(issues),
            "total_issue_instances": total_issue_instances,
            "severity_counts": severity_counts,
        },
        "issues": issues,
    }

    return report


def print_report(report):
    print("\n=== ShamsDAIS Data Quality Firewall Report ===\n")

    summary = report["summary"]

    print(f"Issue types: {summary['issue_types']}")
    print(f"Total issue instances: {summary['total_issue_instances']}")
    print(f"Critical: {summary['severity_counts']['critical']}")
    print(f"High: {summary['severity_counts']['high']}")
    print(f"Medium: {summary['severity_counts']['medium']}")
    print(f"Low: {summary['severity_counts']['low']}")

    print("\nDetected issues:")

    for issue in report["issues"]:
        print(
            f"\n[{issue['severity'].upper()}] {issue['issue_id']} - {issue['title']}"
        )
        print(f"Category: {issue['category']}")
        print(f"Count: {issue['count']}")
        print(f"Recommended action: {issue['recommended_action']}")

        if issue["examples"]:
            print("Examples:")
            for example in issue["examples"][:3]:
                print(f"  - {example}")


def main():
    report = generate_data_quality_report()
    print_report(report)

    output_path = "backend/app/services/data_quality_firewall_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nSaved JSON report to: {output_path}")


if __name__ == "__main__":
    main()

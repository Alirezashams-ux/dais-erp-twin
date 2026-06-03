import os
import psycopg2


DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5433")),
    "dbname": os.getenv("POSTGRES_DB", "dais_erp"),
    "user": os.getenv("POSTGRES_USER", "dais"),
    "password": os.getenv("POSTGRES_PASSWORD", "dais_dev_password"),
}


TABLES = [
    "people",
    "projects",
    "project_members",
    "equipment",
    "datasets",
    "model_assets",
    "experiments",
    "equipment_reservations",
    "purchase_requests",
    "invoices",
    "milestones",
    "publications",
    "erp_events",
    "workflow_events",
    "agent_proposals",
]


QUERIES = {
    "invoices_without_project": """
        SELECT COUNT(*)
        FROM invoices
        WHERE project_id IS NULL;
    """,
    "datasets_without_owner": """
        SELECT COUNT(*)
        FROM datasets
        WHERE owner_person_id IS NULL;
    """,
    "outdated_model_dataset_versions": """
        SELECT COUNT(*)
        FROM model_assets
        WHERE dataset_version_status = 'outdated';
    """,
    "over_budget_purchase_requests": """
        SELECT COUNT(*)
        FROM purchase_requests
        WHERE budget_check_status = 'over_budget';
    """,
    "equipment_reservation_conflict_pairs": """
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
    "pending_agent_proposals": """
        SELECT COUNT(*)
        FROM agent_proposals
        WHERE status = 'pending';
    """,
    "high_risk_agent_proposals": """
        SELECT COUNT(*)
        FROM agent_proposals
        WHERE risk_level = 'high';
    """,
    "erp_events_count": """
        SELECT COUNT(*)
        FROM erp_events;
    """,
    "workflow_events_count": """
        SELECT COUNT(*)
        FROM workflow_events;
    """,
    "workflow_events_missing_hash": """
        SELECT COUNT(*)
        FROM workflow_events
        WHERE event_hash IS NULL OR previous_hash IS NULL;
    """,
}


def connect():
    return psycopg2.connect(**DB_CONFIG)


def main():
    conn = connect()

    try:
        with conn.cursor() as cur:
            print("Table counts:")
            for table in TABLES:
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                count = cur.fetchone()[0]
                print(f"  {table}: {count}")

            print("\nValidation queries:")
            for name, query in QUERIES.items():
                cur.execute(query)
                value = cur.fetchone()[0]
                print(f"  {name}: {value}")

            print("\nSample high-risk proposals:")
            cur.execute("""
                SELECT proposal_id, proposal_type, title, confidence
                FROM agent_proposals
                WHERE risk_level = 'high'
                ORDER BY confidence DESC
                LIMIT 5;
            """)
            rows = cur.fetchall()
            for row in rows:
                print(f"  {row[0]} | {row[1]} | confidence={row[3]} | {row[2]}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

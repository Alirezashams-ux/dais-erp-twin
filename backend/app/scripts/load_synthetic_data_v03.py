import os
import json
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values, Json


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "synthetic_data" / "output_v03"

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5433")),
    "dbname": os.getenv("POSTGRES_DB", "dais_erp"),
    "user": os.getenv("POSTGRES_USER", "dais"),
    "password": os.getenv("POSTGRES_PASSWORD", "dais_dev_password"),
}


CSV_TABLES = {
    "people": {
        "file": "people.csv",
        "columns": [
            "person_id",
            "display_name",
            "role",
            "degree",
            "email",
            "research_area",
            "security_role",
            "actor_type",
        ],
    },
    "projects": {
        "file": "projects.csv",
        "columns": [
            "project_id",
            "project_code",
            "title",
            "theme",
            "status",
            "start_date",
            "end_date",
            "funding_agency",
            "total_budget_krw",
            "spent_krw",
            "pi_person_id",
        ],
    },
    "project_members": {
        "file": "project_members.csv",
        "columns": [
            "project_id",
            "person_id",
            "project_role",
            "allocation_percent",
        ],
    },
    "equipment": {
        "file": "equipment.csv",
        "columns": [
            "equipment_id",
            "asset_code",
            "name",
            "category",
            "location",
            "status",
            "utilization_rate",
            "maintenance_due_date",
        ],
    },
    "datasets": {
        "file": "datasets.csv",
        "columns": [
            "dataset_id",
            "dataset_code",
            "project_id",
            "owner_person_id",
            "title",
            "data_type",
            "version",
            "sensitivity_level",
            "row_count",
            "file_count",
            "quality_score",
            "storage_path",
            "approval_status",
        ],
    },
    "model_assets": {
        "file": "model_assets.csv",
        "columns": [
            "model_id",
            "model_code",
            "project_id",
            "dataset_id",
            "name",
            "model_type",
            "version",
            "dataset_version_status",
            "accuracy",
            "f1_score",
            "false_alarm_rate",
            "deployment_status",
            "code_commit",
            "environment_hash",
            "artifact_path",
        ],
    },
    "experiments": {
        "file": "experiments.csv",
        "columns": [
            "experiment_id",
            "experiment_code",
            "project_id",
            "dataset_id",
            "model_id",
            "equipment_id",
            "researcher_person_id",
            "status",
            "started_at",
            "completed_at",
            "failed_at",
            "failure_reason",
            "result_json",
            "reproducibility_score",
        ],
        "json_columns": ["result_json"],
    },
    "equipment_reservations": {
        "file": "equipment_reservations.csv",
        "columns": [
            "reservation_id",
            "equipment_id",
            "experiment_id",
            "reserved_by_person_id",
            "start_time",
            "end_time",
            "status",
        ],
    },
    "purchase_requests": {
        "file": "purchase_requests.csv",
        "columns": [
            "purchase_request_id",
            "request_code",
            "project_id",
            "requester_person_id",
            "item_name",
            "amount_krw",
            "status",
            "approval_required",
            "budget_check_status",
            "created_at",
        ],
    },
    "invoices": {
        "file": "invoices.csv",
        "columns": [
            "invoice_id",
            "invoice_code",
            "supplier_name",
            "business_registration_no",
            "project_id",
            "purchase_request_id",
            "amount_krw",
            "vat_krw",
            "issue_date",
            "source_file",
            "confidence",
        ],
    },
    "milestones": {
        "file": "milestones.csv",
        "columns": [
            "milestone_id",
            "project_id",
            "milestone_name",
            "due_date",
            "status",
            "risk_score",
        ],
    },
    "publications": {
        "file": "publications.csv",
        "columns": [
            "publication_id",
            "title",
            "project_id",
            "dataset_id",
            "model_id",
            "experiment_id",
            "authors",
            "type",
            "status",
            "target_venue",
            "year",
            "reproducibility_package_status",
            "doi_like_id",
            "code_commit",
            "artifact_path",
        ],
    },
}


JSONL_TABLES = {
    "erp_events": {
        "file": "erp_events.jsonl",
        "columns": [
            "event_id",
            "event_type",
            "entity_type",
            "entity_id",
            "payload",
            "source_uri",
            "confidence",
            "created_by",
            "previous_hash",
            "event_hash",
            "created_at",
        ],
        "json_columns": ["payload"],
    },
    "workflow_events": {
        "file": "workflow_events.jsonl",
        "columns": [
            "workflow_event_id",
            "event_type",
            "entity_type",
            "entity_id",
            "actor_id",
            "actor_type",
            "role",
            "payload",
            "timestamp",
            "previous_hash",
            "event_hash",
        ],
        "json_columns": ["payload"],
    },
}


AGENT_PROPOSALS = {
    "file": "agent_proposals.json",
    "columns": [
        "proposal_id",
        "proposal_type",
        "title",
        "affected_entity_type",
        "affected_entity_id",
        "risk_level",
        "confidence",
        "evidence",
        "status",
        "created_at",
        "requires_approval",
    ],
    "json_columns": ["evidence"],
}


DELETE_ORDER = [
    "agent_proposals",
    "workflow_events",
    "erp_events",
    "publications",
    "milestones",
    "invoices",
    "purchase_requests",
    "equipment_reservations",
    "experiments",
    "model_assets",
    "datasets",
    "equipment",
    "project_members",
    "projects",
    "people",
]


def connect():
    return psycopg2.connect(**DB_CONFIG)


def clean_value(value):
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return value

    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

    return value


def clean_json_value(value):
    value = clean_value(value)

    if value is None:
        return Json(None)

    if isinstance(value, (dict, list)):
        return Json(value)

    if isinstance(value, str):
        try:
            return Json(json.loads(value))
        except json.JSONDecodeError:
            return Json({"raw": value})

    return Json(value)


def prepare_dataframe(df, expected_columns, json_columns=None):
    json_columns = set(json_columns or [])

    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[expected_columns]

    rows = []
    for _, row in df.iterrows():
        converted_row = []

        for col in expected_columns:
            value = row[col]

            if col in json_columns:
                converted_row.append(clean_json_value(value))
            else:
                converted_row.append(clean_value(value))

        rows.append(tuple(converted_row))

    return rows


def insert_rows(conn, table_name, columns, rows):
    if not rows:
        print(f"Loaded {table_name}: 0 rows")
        return

    column_sql = ", ".join(columns)
    query = f"INSERT INTO {table_name} ({column_sql}) VALUES %s"

    with conn.cursor() as cur:
        execute_values(cur, query, rows, page_size=500)


def clear_tables(conn):
    with conn.cursor() as cur:
        for table in DELETE_ORDER:
            cur.execute(f"DELETE FROM {table};")

    conn.commit()
    print("Cleared existing tables.")


def load_csv_table(conn, table_name, config):
    path = DATA_DIR / config["file"]

    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    rows = prepare_dataframe(
        df=df,
        expected_columns=config["columns"],
        json_columns=config.get("json_columns", []),
    )

    insert_rows(conn, table_name, config["columns"], rows)
    print(f"Loaded {table_name}: {len(rows)} rows")


def load_jsonl_table(conn, table_name, config):
    path = DATA_DIR / config["file"]

    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    df = pd.DataFrame(records)

    rows = prepare_dataframe(
        df=df,
        expected_columns=config["columns"],
        json_columns=config.get("json_columns", []),
    )

    insert_rows(conn, table_name, config["columns"], rows)
    print(f"Loaded {table_name}: {len(rows)} rows")


def load_agent_proposals(conn):
    path = DATA_DIR / AGENT_PROPOSALS["file"]

    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    records = json.loads(path.read_text(encoding="utf-8"))
    df = pd.DataFrame(records)

    rows = prepare_dataframe(
        df=df,
        expected_columns=AGENT_PROPOSALS["columns"],
        json_columns=AGENT_PROPOSALS.get("json_columns", []),
    )

    insert_rows(conn, "agent_proposals", AGENT_PROPOSALS["columns"], rows)
    print(f"Loaded agent_proposals: {len(rows)} rows")


def print_counts(conn):
    print("\nFinal table counts:")

    with conn.cursor() as cur:
        for table in reversed(DELETE_ORDER):
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"  {table}: {count}")


def main():
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Loading data from: {DATA_DIR}")
    print(f"Database host: {DB_CONFIG['host']}")
    print(f"Database port: {DB_CONFIG['port']}")
    print(f"Database name: {DB_CONFIG['dbname']}")

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory does not exist: {DATA_DIR}")

    conn = connect()

    try:
        clear_tables(conn)

        for table_name, config in CSV_TABLES.items():
            load_csv_table(conn, table_name, config)

        for table_name, config in JSONL_TABLES.items():
            load_jsonl_table(conn, table_name, config)

        load_agent_proposals(conn)

        conn.commit()
        print_counts(conn)
        print("\nData load complete.")

    except Exception:
        conn.rollback()
        print("\nData load failed. Rolled back transaction.")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main() 

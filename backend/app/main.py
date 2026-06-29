import os
from decimal import Decimal
from datetime import date, datetime
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.app.services.data_quality_firewall import generate_data_quality_report


DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5433")),
    "dbname": os.getenv("POSTGRES_DB", "dais_erp"),
    "user": os.getenv("POSTGRES_USER", "dais"),
    "password": os.getenv("POSTGRES_PASSWORD", "dais_dev_password"),
}


app = FastAPI(
    title="ShamsDAIS / DAIS-ERP Twin API",
    description="Minimal backend API for the secure agentic ERP Twin demo.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def connect():
    return psycopg2.connect(**DB_CONFIG)


def sanitize(value: Any):
    """
    Convert PostgreSQL/Python objects into JSON-safe values.
    FastAPI can handle many types, but this keeps our API predictable.
    """
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, list):
        return [sanitize(item) for item in value]

    if isinstance(value, dict):
        return {key: sanitize(val) for key, val in value.items()}

    return value


def fetch_all(query: str, params=None):
    conn = connect()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or {})
            rows = cur.fetchall()
            return sanitize([dict(row) for row in rows])

    finally:
        conn.close()


def fetch_one(query: str, params=None):
    conn = connect()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or {})
            row = cur.fetchone()
            return sanitize(dict(row)) if row else None

    finally:
        conn.close()


@app.get("/")
def root():
    return {
        "system": "ShamsDAIS / DAIS-ERP Twin",
        "message": "Minimal FastAPI backend is running.",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    try:
        result = fetch_one("SELECT 1 AS ok;")
        return {
            "status": "healthy",
            "database": "connected",
            "db_result": result,
            "db_host": DB_CONFIG["host"],
            "db_port": DB_CONFIG["port"],
            "db_name": DB_CONFIG["dbname"],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {exc}",
        )


@app.get("/summary")
def summary():
    """
    High-level ERP table counts for the first demo.
    """
    tables = [
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

    counts = {}

    conn = connect()
    try:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                counts[table] = cur.fetchone()[0]

    finally:
        conn.close()

    return {
        "system": "ShamsDAIS / DAIS-ERP Twin",
        "summary": counts,
    }


@app.get("/projects")
def get_projects():
    return fetch_all(
        """
        SELECT
            project_id,
            project_code,
            title,
            theme,
            status,
            start_date,
            end_date,
            funding_agency,
            total_budget_krw,
            spent_krw,
            ROUND((spent_krw::numeric / NULLIF(total_budget_krw, 0)) * 100, 2) AS spent_percent
        FROM projects
        ORDER BY project_id;
        """
    )


@app.get("/projects/{project_id}")
def get_project_detail(project_id: str):
    project = fetch_one(
        """
        SELECT *
        FROM projects
        WHERE project_id = %(project_id)s;
        """,
        {"project_id": project_id},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    datasets = fetch_all(
        """
        SELECT dataset_id, dataset_code, title, data_type, version, sensitivity_level, quality_score
        FROM datasets
        WHERE project_id = %(project_id)s
        ORDER BY dataset_id;
        """,
        {"project_id": project_id},
    )

    models = fetch_all(
        """
        SELECT model_id, model_code, name, model_type, version,
               dataset_version_status, accuracy, f1_score, deployment_status
        FROM model_assets
        WHERE project_id = %(project_id)s
        ORDER BY model_id;
        """,
        {"project_id": project_id},
    )

    experiments = fetch_all(
        """
        SELECT experiment_id, experiment_code, status, started_at, completed_at,
               reproducibility_score
        FROM experiments
        WHERE project_id = %(project_id)s
        ORDER BY experiment_id;
        """,
        {"project_id": project_id},
    )

    purchases = fetch_all(
        """
        SELECT purchase_request_id, request_code, item_name, amount_krw,
               status, budget_check_status, created_at
        FROM purchase_requests
        WHERE project_id = %(project_id)s
        ORDER BY purchase_request_id;
        """,
        {"project_id": project_id},
    )

    return {
        "project": project,
        "datasets": datasets,
        "models": models,
        "experiments": experiments,
        "purchase_requests": purchases,
    }


@app.get("/data-quality/report")
def data_quality_report():
    """
    Run the Data Quality Firewall and return the full report.
    """
    report = generate_data_quality_report()
    return sanitize(report)


@app.get("/data-quality/summary")
def data_quality_summary():
    """
    Short version of the Data Quality Firewall report.
    """
    report = generate_data_quality_report()
    return sanitize(report["summary"])


@app.get("/agent-proposals")
def get_agent_proposals(
    status: str | None = Query(default=None, description="Example: pending"),
    risk_level: str | None = Query(default=None, description="Example: high"),
    limit: int = Query(default=50, ge=1, le=200),
):
    query = """
        SELECT
            proposal_id,
            proposal_type,
            title,
            affected_entity_type,
            affected_entity_id,
            risk_level,
            confidence,
            status,
            created_at,
            requires_approval
        FROM agent_proposals
        WHERE 1 = 1
    """

    params = {"limit": limit}

    if status:
        query += " AND status = %(status)s"
        params["status"] = status

    if risk_level:
        query += " AND risk_level = %(risk_level)s"
        params["risk_level"] = risk_level

    query += """
        ORDER BY
            CASE risk_level
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
                ELSE 5
            END,
            confidence DESC NULLS LAST
        LIMIT %(limit)s;
    """

    return fetch_all(query, params)


@app.get("/agent-proposals/high-risk")
def get_high_risk_agent_proposals():
    return fetch_all(
        """
        SELECT
            proposal_id,
            proposal_type,
            title,
            affected_entity_type,
            affected_entity_id,
            risk_level,
            confidence,
            status,
            evidence,
            created_at
        FROM agent_proposals
        WHERE status = 'pending'
          AND risk_level = 'high'
        ORDER BY confidence DESC NULLS LAST;
        """
    )


@app.get("/events/summary")
def event_summary():
    erp_events = fetch_all(
        """
        SELECT event_type, COUNT(*) AS count
        FROM erp_events
        GROUP BY event_type
        ORDER BY count DESC;
        """
    )

    workflow_events = fetch_all(
        """
        SELECT event_type, COUNT(*) AS count
        FROM workflow_events
        GROUP BY event_type
        ORDER BY count DESC;
        """
    )

    workflow_hash_check = fetch_one(
        """
        SELECT COUNT(*) AS missing_hash_count
        FROM workflow_events
        WHERE previous_hash IS NULL
           OR event_hash IS NULL;
        """
    )

    return {
        "erp_events": erp_events,
        "workflow_events": workflow_events,
        "workflow_hash_check": workflow_hash_check,
    }


@app.get("/lineage/project/{project_id}")
def project_lineage(project_id: str):
    """
    Show Project → Dataset → Model → Experiment → Publication links.
    This is important for the ERP Twin / research reproducibility demo.
    """
    project = fetch_one(
        """
        SELECT project_id, project_code, title, theme
        FROM projects
        WHERE project_id = %(project_id)s;
        """,
        {"project_id": project_id},
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lineage = fetch_all(
        """
        SELECT
            d.dataset_id,
            d.dataset_code,
            d.title AS dataset_title,
            m.model_id,
            m.model_code,
            m.name AS model_name,
            e.experiment_id,
            e.experiment_code,
            e.status AS experiment_status,
            p.publication_id,
            p.title AS publication_title,
            p.reproducibility_package_status
        FROM datasets d
        LEFT JOIN model_assets m ON m.dataset_id = d.dataset_id
        LEFT JOIN experiments e ON e.model_id = m.model_id
        LEFT JOIN publications p ON p.experiment_id = e.experiment_id
        WHERE d.project_id = %(project_id)s
        ORDER BY d.dataset_id, m.model_id, e.experiment_id, p.publication_id;
        """,
        {"project_id": project_id},
    )

    return {
        "project": project,
        "lineage": lineage,
    }


@app.get("/equipment/conflicts")
def equipment_conflicts():
    return fetch_all(
        """
        SELECT
            a.equipment_id,
            eq.name AS equipment_name,
            a.reservation_id AS reservation_a,
            b.reservation_id AS reservation_b,
            a.start_time AS a_start,
            a.end_time AS a_end,
            b.start_time AS b_start,
            b.end_time AS b_end,
            a.experiment_id AS experiment_a,
            b.experiment_id AS experiment_b
        FROM equipment_reservations a
        JOIN equipment_reservations b
          ON a.equipment_id = b.equipment_id
         AND a.reservation_id < b.reservation_id
         AND a.status = 'confirmed'
         AND b.status = 'confirmed'
         AND a.start_time < b.end_time
         AND b.start_time < a.end_time
        LEFT JOIN equipment eq ON a.equipment_id = eq.equipment_id
        ORDER BY a.start_time;
        """
    )

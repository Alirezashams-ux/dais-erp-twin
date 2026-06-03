DROP TABLE IF EXISTS agent_proposals CASCADE;
DROP TABLE IF EXISTS workflow_events CASCADE;
DROP TABLE IF EXISTS erp_events CASCADE;
DROP TABLE IF EXISTS publications CASCADE;
DROP TABLE IF EXISTS milestones CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS purchase_requests CASCADE;
DROP TABLE IF EXISTS equipment_reservations CASCADE;
DROP TABLE IF EXISTS experiments CASCADE;
DROP TABLE IF EXISTS model_assets CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS project_members CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
CREATE TABLE people (
    person_id TEXT PRIMARY KEY,
    display_name TEXT,
    role TEXT,
    degree TEXT,
    email TEXT,
    research_area TEXT,
    security_role TEXT
);
DROP TABLE IF EXISTS people CASCADE;
CREATE TABLE people (
    person_id TEXT PRIMARY KEY,
    display_name TEXT,
    role TEXT,
    degree TEXT,
    email TEXT,
    research_area TEXT,
    security_role TEXT,
    actor_type TEXT
);
CREATE TABLE people (
    person_id TEXT PRIMARY KEY,
    display_name TEXT,
    role TEXT,
    degree TEXT,
    email TEXT,
    research_area TEXT,
    security_role TEXT
);

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    project_code TEXT UNIQUE,
    title TEXT,
    theme TEXT,
    status TEXT,
    start_date DATE,
    end_date DATE,
    funding_agency TEXT,
    total_budget_krw BIGINT,
    spent_krw BIGINT,
    pi_person_id TEXT REFERENCES people(person_id)
);

CREATE TABLE project_members (
    project_id TEXT REFERENCES projects(project_id),
    person_id TEXT REFERENCES people(person_id),
    project_role TEXT,
    allocation_percent NUMERIC,
    PRIMARY KEY (project_id, person_id, project_role)
);

CREATE TABLE equipment (
    equipment_id TEXT PRIMARY KEY,
    asset_code TEXT,
    name TEXT,
    category TEXT,
    location TEXT,
    status TEXT,
    utilization_rate NUMERIC,
    maintenance_due_date DATE
);

CREATE TABLE datasets (
    dataset_id TEXT PRIMARY KEY,
    dataset_code TEXT,
    project_id TEXT REFERENCES projects(project_id),
    owner_person_id TEXT REFERENCES people(person_id),
    title TEXT,
    data_type TEXT,
    version TEXT,
    sensitivity_level TEXT,
    row_count BIGINT,
    file_count BIGINT,
    quality_score NUMERIC,
    storage_path TEXT,
    approval_status TEXT
);

CREATE TABLE model_assets (
    model_id TEXT PRIMARY KEY,
    model_code TEXT,
    project_id TEXT REFERENCES projects(project_id),
    dataset_id TEXT REFERENCES datasets(dataset_id),
    name TEXT,
    model_type TEXT,
    version TEXT,
    dataset_version_status TEXT,
    accuracy NUMERIC,
    f1_score NUMERIC,
    false_alarm_rate NUMERIC,
    deployment_status TEXT,
    code_commit TEXT,
    environment_hash TEXT,
    artifact_path TEXT
);

CREATE TABLE experiments (
    experiment_id TEXT PRIMARY KEY,
    experiment_code TEXT,
    project_id TEXT REFERENCES projects(project_id),
    dataset_id TEXT REFERENCES datasets(dataset_id),
    model_id TEXT REFERENCES model_assets(model_id),
    equipment_id TEXT REFERENCES equipment(equipment_id),
    researcher_person_id TEXT REFERENCES people(person_id),
    status TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    failure_reason TEXT,
    result_json JSONB,
    reproducibility_score NUMERIC
);

CREATE TABLE equipment_reservations (
    reservation_id TEXT PRIMARY KEY,
    equipment_id TEXT REFERENCES equipment(equipment_id),
    experiment_id TEXT REFERENCES experiments(experiment_id),
    reserved_by_person_id TEXT REFERENCES people(person_id),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    status TEXT
);

CREATE TABLE purchase_requests (
    purchase_request_id TEXT PRIMARY KEY,
    request_code TEXT,
    project_id TEXT REFERENCES projects(project_id),
    requester_person_id TEXT REFERENCES people(person_id),
    item_name TEXT,
    amount_krw BIGINT,
    status TEXT,
    approval_required BOOLEAN,
    budget_check_status TEXT,
    created_at TIMESTAMPTZ
);

CREATE TABLE invoices (
    invoice_id TEXT PRIMARY KEY,
    invoice_code TEXT,
    supplier_name TEXT,
    business_registration_no TEXT,
    project_id TEXT REFERENCES projects(project_id),
    purchase_request_id TEXT REFERENCES purchase_requests(purchase_request_id),
    amount_krw BIGINT,
    vat_krw BIGINT,
    issue_date DATE,
    source_file TEXT,
    confidence NUMERIC
);

CREATE TABLE milestones (
    milestone_id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(project_id),
    milestone_name TEXT,
    due_date DATE,
    status TEXT,
    risk_score NUMERIC
);

CREATE TABLE publications (
    publication_id TEXT PRIMARY KEY,
    title TEXT,
    project_id TEXT REFERENCES projects(project_id),
    dataset_id TEXT REFERENCES datasets(dataset_id),
    model_id TEXT REFERENCES model_assets(model_id),
    experiment_id TEXT REFERENCES experiments(experiment_id),
    authors TEXT,
    type TEXT,
    status TEXT,
    target_venue TEXT,
    year INTEGER,
    reproducibility_package_status TEXT,
    doi_like_id TEXT,
    code_commit TEXT,
    artifact_path TEXT
);

CREATE TABLE erp_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT,
    entity_type TEXT,
    entity_id TEXT,
    payload JSONB,
    source_uri TEXT,
    confidence NUMERIC,
    created_by TEXT,
    previous_hash TEXT,
    event_hash TEXT,
    created_at TIMESTAMPTZ
);

CREATE TABLE workflow_events (
    workflow_event_id TEXT PRIMARY KEY,
    event_type TEXT,
    entity_type TEXT,
    entity_id TEXT,
    actor_id TEXT,
    actor_type TEXT,
    role TEXT,
    payload JSONB,
    timestamp TIMESTAMPTZ,
    previous_hash TEXT,
    event_hash TEXT
);

CREATE TABLE agent_proposals (
    proposal_id TEXT PRIMARY KEY,
    proposal_type TEXT,
    title TEXT,
    affected_entity_type TEXT,
    affected_entity_id TEXT,
    risk_level TEXT,
    confidence NUMERIC,
    evidence JSONB,
    status TEXT,
    created_at TIMESTAMPTZ,
    requires_approval BOOLEAN
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_datasets_project_id ON datasets(project_id);
CREATE INDEX idx_models_project_id ON model_assets(project_id);
CREATE INDEX idx_models_dataset_id ON model_assets(dataset_id);
CREATE INDEX idx_experiments_project_id ON experiments(project_id);
CREATE INDEX idx_experiments_model_id ON experiments(model_id);
CREATE INDEX idx_equipment_reservations_equipment_id ON equipment_reservations(equipment_id);
CREATE INDEX idx_purchase_requests_project_id ON purchase_requests(project_id);
CREATE INDEX idx_purchase_requests_status ON purchase_requests(status);
CREATE INDEX idx_invoices_project_id ON invoices(project_id);
CREATE INDEX idx_erp_events_event_type ON erp_events(event_type);
CREATE INDEX idx_workflow_events_event_type ON workflow_events(event_type);
CREATE INDEX idx_agent_proposals_status ON agent_proposals(status);
CREATE INDEX idx_agent_proposals_risk_level ON agent_proposals(risk_level);

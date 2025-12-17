
-- keep extensions
create extension if not exists "pgcrypto";

-- === CORE REFERENCE ===
create table if not exists units (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  created_at timestamptz default now()
);


create table if not exists strategic_goals (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  title text not null,
  description text,
  category text,
  created_at timestamptz default now()
);

create table if not exists people (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  title text,
  unit_id uuid not null references units(id),
  created_at timestamptz default now(),
  constraint uq_people_unit_name unique (unit_id, name)
);

create table if not exists teams (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  unit_id uuid not null references units(id),
  manager_id uuid,
  created_at timestamptz default now(),
  constraint uq_teams_unit_name unique (unit_id, name)
);

create table if not exists team_members (
  team_id uuid references teams(id) on delete cascade,
  person_id uuid references people(id) on delete cascade,
  role text,
  primary key (team_id, person_id)
);

-- === GOALS (PERSONAL + TEAM) ===
create table if not exists personal_goals (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references people(id),
  unit_id uuid not null references units(id),
  text text not null,
  normalized_text text,
  status text check (status in ('planned','in_progress','at_risk','blocked','complete')) default 'planned',
  percent_complete numeric check (percent_complete between 0 and 100) default 0,
  entered_by uuid,
  last_reviewed_at timestamptz,
  created_at timestamptz default now()
);

create table if not exists team_goals (
  id uuid primary key default gen_random_uuid(),
  team_id uuid not null references teams(id),
  text text not null,
  normalized_text text,
  status text check (status in ('planned','in_progress','at_risk','blocked','complete')) default 'planned',
  percent_complete numeric check (percent_complete between 0 and 100) default 0,
  created_at timestamptz default now()
);

-- one alignment table for personal OR team targets
create table if not exists goal_alignments (
  id uuid primary key default gen_random_uuid(),
  strategic_goal_id uuid not null references strategic_goals(id),
  target_type text check (target_type in ('personal','team')) not null,
  personal_goal_id uuid references personal_goals(id),
  team_goal_id uuid references team_goals(id),
  confidence numeric,
  status text check (status in ('suggested','accepted','rejected','needs_review')) default 'suggested',
  reviewer_id uuid,
  decided_at timestamptz,
  note text
);

-- === DOC INGEST + AI ===
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  owner_type text check (owner_type in ('person','team')) not null,
  owner_id uuid not null,
  source text,           -- upload/link/paste
  file_url text,
  mime_type text,
  text_content text,
  imported_at timestamptz default now()
);

create table if not exists extracted_goals (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references documents(id) on delete cascade,
  normalized_text text not null,
  suggested_code text,           -- e.g., 'A1'
  strategic_goal_id uuid,        -- resolved id if mapped
  confidence numeric,
  status text check (status in ('suggested','approved','rejected','created')) default 'suggested',
  reviewer_id uuid,
  decided_at timestamptz,
  note text
);

create table if not exists audit_log (
  id bigserial primary key,
  actor_id uuid,
  action text,
  entity text,
  entity_id uuid,
  before_json jsonb,
  after_json jsonb,
  created_at timestamptz default now()
);

-- Enable RLS + permissive policy on all project tables (public schema)
-- Run again is safe (drops policy first).
do $$
declare
  tbl text;
  tbls text[] := array[
    'units','strategic_goals','people','teams','team_members',
    'personal_goals','team_goals','goal_alignments',
    'documents','extracted_goals','audit_log'
  ];
begin
  foreach tbl in array tbls loop
    execute format('alter table public.%I enable row level security;', tbl);
    execute format('drop policy if exists dev_all on public.%I;', tbl);
    execute format('create policy dev_all on public.%I for all to public using (true) with check (true);', tbl);
  end loop;
end $$;


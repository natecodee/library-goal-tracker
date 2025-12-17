# Infra SQL

Apply in Supabase Studio → SQL Editor in this order:
1) 000_init_schema.sql
2) 010_seed_dev.sql
3) 020_rls_dev_open.sql (dev only)
4) 030_sanity_checks.sql

For prod, replace 020 with real RLS policies.


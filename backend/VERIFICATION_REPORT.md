# Verification Report - End-to-End Test Readiness

## 1. Route Verification ✅

All routes in TEST_EXAMPLES.md match actual implementation:

- ✅ `GET /api/strategic-goals` 
  - Router: `catalog.py` (no prefix) + main.py adds `/api`
  - Actual route: `/api/strategic-goals`

- ✅ `GET /api/extracted-goals?document_id=...`
  - Router: `extracted_goals.py` (prefix="/extracted-goals") + main.py adds `/api`
  - Actual route: `/api/extracted-goals`

- ✅ `PATCH /api/extracted-goals/{id}`
  - Same router as above
  - Actual route: `/api/extracted-goals/{id}`

- ✅ `POST /api/ai/align-and-store`
  - Router: `ai_routes.py` (prefix="/ai") + main.py adds `/api`
  - Actual route: `/api/ai/align-and-store`

**All routes are correct. No changes needed.**

## 2. Status Values Verification ✅

**Database Schema** (from `000_init_schema.sql` line 104):
```sql
status text check (status in ('suggested','approved','rejected','created')) default 'suggested'
```

**Backend Code** (from `extracted_goals.py` line 24):
```python
VALID_STATUSES = {"suggested", "approved", "rejected", "created"}
```

**Test Examples**: Use `"approved"` and `"rejected"` ✅

**Status**: All consistent. Backend enforces `approved` (not `accepted`), which matches DB schema.

## 3. normalized_text NOT NULL Verification ✅

### In `/api/ai/align-and-store` (ai_routes.py line 137):
```python
rows.append({
    "document_id": payload.document_id,
    "goal_text": g,
    "normalized_text": normalize_goal(g),  # REQUIRED (NOT NULL)
    ...
})
```
✅ **Always sets normalized_text** - derived from goal_text via `normalize_goal()` function.

### In `PATCH /api/extracted-goals/{id}` (extracted_goals.py lines 81-83):
```python
if "goal_text" in update_data:
    if update_data["goal_text"]:
        update_data["normalized_text"] = normalize_goal(update_data["goal_text"])
```
✅ **Automatically updates normalized_text** when goal_text is updated.

**Status**: Both endpoints correctly handle normalized_text. No changes needed.

## 4. Complete Workflow Test

See updated section 4 in TEST_EXAMPLES.md - now includes:
- Error handling (checks for empty results)
- Progress messages
- Verification step that re-lists goals to confirm changes
- All placeholders replaced with actual variable references

## 5. Next Steps Implementation

Ready to implement after tests pass:
1. POST /api/extracted-goals/{id}/decision endpoint
2. GET /api/extracted-goals with status filter


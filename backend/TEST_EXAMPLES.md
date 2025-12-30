# PowerShell Test Examples for Extracted Goals Endpoints

These examples assume you're in the `backend` directory with the virtual environment activated.

## Setup
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

## 1. Get Strategic Goals Catalog

```powershell
Invoke-RestMethod -Method Get `
  -Uri "http://127.0.0.1:8000/api/strategic-goals" `
  -ContentType "application/json"
```

## 2. List Extracted Goals for a Document

Replace `{document_id}` with an actual UUID from your documents table.

```powershell
$documentId = "7074f07d-6528-4953-8d14-ffb11d25195d"

Invoke-RestMethod -Method Get `
  -Uri "http://127.0.0.1:8000/api/extracted-goals?document_id=$documentId" `
  -ContentType "application/json"
```

## 3. Update an Extracted Goal

First, get an extracted goal ID from the list endpoint above, then use it here.

### Example 3a: Approve a goal and set strategic_goal_id

```powershell
$goalId = "YOUR_EXTRACTED_GOAL_ID_HERE"
$strategicGoalId = "YOUR_STRATEGIC_GOAL_ID_HERE"
$reviewerId = "00000000-0000-0000-0000-000000000001"

$body = @{
    status = "approved"
    strategic_goal_id = $strategicGoalId
    reviewer_id = $reviewerId
    note = "This goal aligns well with our strategic priorities."
} | ConvertTo-Json

Invoke-RestMethod -Method Patch `
  -Uri "http://127.0.0.1:8000/api/extracted-goals/$goalId" `
  -ContentType "application/json" `
  -Body $body
```

### Example 3b: Reject a goal with a note

```powershell
$goalId = "YOUR_EXTRACTED_GOAL_ID_HERE"
$reviewerId = "00000000-0000-0000-0000-000000000001"

$body = @{
    status = "rejected"
    reviewer_id = $reviewerId
    note = "This goal is too vague and needs more specificity."
} | ConvertTo-Json

Invoke-RestMethod -Method Patch `
  -Uri "http://127.0.0.1:8000/api/extracted-goals/$goalId" `
  -ContentType "application/json" `
  -Body $body
```

### Example 3c: Update goal text (which also updates normalized_text)

```powershell
$goalId = "YOUR_EXTRACTED_GOAL_ID_HERE"

$body = @{
    goal_text = "Improve library onboarding documentation and processes"
} | ConvertTo-Json

Invoke-RestMethod -Method Patch `
  -Uri "http://127.0.0.1:8000/api/extracted-goals/$goalId" `
  -ContentType "application/json" `
  -Body $body
```

### Example 3d: Update multiple fields at once

```powershell
$goalId = "YOUR_EXTRACTED_GOAL_ID_HERE"
$strategicGoalId = "YOUR_STRATEGIC_GOAL_ID_HERE"
$reviewerId = "00000000-0000-0000-0000-000000000001"

$body = @{
    status = "approved"
    strategic_goal_id = $strategicGoalId
    suggested_code = "A1"
    confidence = 0.85
    reviewer_id = $reviewerId
    note = "High confidence match after review."
} | ConvertTo-Json

Invoke-RestMethod -Method Patch `
  -Uri "http://127.0.0.1:8000/api/extracted-goals/$goalId" `
  -ContentType "application/json" `
  -Body $body
```

## 4. Complete Workflow Example (Copy/Paste Ready)

```powershell
# Step 1: Define document ID (REQUIRED - change this to your actual document ID)
$documentId = "7074f07d-6528-4953-8d14-ffb11d25195d"

# Validate document ID is set
if ([string]::IsNullOrEmpty($documentId)) {
    Write-Host "ERROR: documentId is not defined. Please set it at the top of this script." -ForegroundColor Red
    return
}

# Step 2: Extract and align goals (this will delete previous extracted goals for this document)
Write-Host "Extracting and aligning goals..."
try {
    $alignResult = Invoke-RestMethod `
        -Method Post `
        -Uri "http://127.0.0.1:8000/api/ai/align-and-store" `
        -ContentType "application/json" `
        -Body (@{ document_id = $documentId } | ConvertTo-Json)
    Write-Host "Inserted $($alignResult.inserted) goals" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to extract and align goals. $_" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Red
    return
}

# Step 3: List extracted goals
Write-Host "`nFetching extracted goals..."
try {
    $goals = Invoke-RestMethod `
        -Method Get `
        -Uri "http://127.0.0.1:8000/api/extracted-goals?document_id=$documentId" `
        -ContentType "application/json"
} catch {
    Write-Host "ERROR: Failed to fetch extracted goals. $_" -ForegroundColor Red
    return
}

if ($goals.items.Count -eq 0) {
    Write-Host "No extracted goals found. Make sure the document has text content." -ForegroundColor Yellow
    return
}

Write-Host "Found $($goals.items.Count) extracted goals" -ForegroundColor Green
$firstGoalId = $goals.items[0].id
Write-Host "First goal ID: $firstGoalId"

# Step 4: Get strategic goals catalog
Write-Host "`nFetching strategic goals catalog..."
try {
    $strategicGoals = Invoke-RestMethod `
        -Method Get `
        -Uri "http://127.0.0.1:8000/api/strategic-goals" `
        -ContentType "application/json"
} catch {
    Write-Host "ERROR: Failed to fetch strategic goals. $_" -ForegroundColor Red
    return
}

if ($strategicGoals.items.Count -eq 0) {
    Write-Host "No strategic goals found in catalog." -ForegroundColor Yellow
    return
}

$firstStrategicGoalId = $strategicGoals.items[0].id
Write-Host "First strategic goal ID: $firstStrategicGoalId"

# Step 5: Approve the first goal
Write-Host "`nApproving first extracted goal..."
$reviewerId = "00000000-0000-0000-0000-000000000001"
$body = @{
    status = "approved"
    strategic_goal_id = $firstStrategicGoalId
    reviewer_id = $reviewerId
    note = "Approved after review - aligns with strategic priorities"
} | ConvertTo-Json

try {
    $updateResult = Invoke-RestMethod `
        -Method Patch `
        -Uri "http://127.0.0.1:8000/api/extracted-goals/$firstGoalId" `
        -ContentType "application/json" `
        -Body $body
    Write-Host "Goal updated successfully. Status: $($updateResult.updated.status)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to update goal. $_" -ForegroundColor Red
    return
}

# Step 6: Verify changes by re-listing
Write-Host "`nVerifying changes..."
try {
    $goalsAfter = Invoke-RestMethod `
        -Method Get `
        -Uri "http://127.0.0.1:8000/api/extracted-goals?document_id=$documentId" `
        -ContentType "application/json"
} catch {
    Write-Host "ERROR: Failed to verify changes. $_" -ForegroundColor Red
    return
}

$updatedGoal = $goalsAfter.items | Where-Object { $_.id -eq $firstGoalId }
Write-Host "`nUpdated goal details:" -ForegroundColor Cyan
Write-Host "  Status: $($updatedGoal.status)"
Write-Host "  Strategic Goal ID: $($updatedGoal.strategic_goal_id)"
Write-Host "  Reviewer ID: $($updatedGoal.reviewer_id)"
Write-Host "  Decided At: $($updatedGoal.decided_at)"
Write-Host "  Note: $($updatedGoal.note)"
```

## 5. Filter Extracted Goals by Status

```powershell
$documentId = "7074f07d-6528-4953-8d14-ffb11d25195d"

# Get only suggested goals
Invoke-RestMethod -Method Get `
  -Uri "http://127.0.0.1:8000/api/extracted-goals?document_id=$documentId&status=suggested" `
  -ContentType "application/json"

# Get only approved goals
Invoke-RestMethod -Method Get `
  -Uri "http://127.0.0.1:8000/api/extracted-goals?document_id=$documentId&status=approved" `
  -ContentType "application/json"
```

## 6. Make a Decision (Convenience Endpoint)

This endpoint is a convenience wrapper around PATCH that automatically sets `decided_at` when approving/rejecting.

### Example 6a: Approve with decision endpoint

```powershell
$goalId = "YOUR_EXTRACTED_GOAL_ID_HERE"
$strategicGoalId = "YOUR_STRATEGIC_GOAL_ID_HERE"
$reviewerId = "00000000-0000-0000-0000-000000000001"

$body = @{
    status = "approved"
    strategic_goal_id = $strategicGoalId
    reviewer_id = $reviewerId
    note = "Approved via decision endpoint"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/extracted-goals/$goalId/decision" `
  -ContentType "application/json" `
  -Body $body
```

### Example 6b: Reject with decision endpoint

```powershell
$goalId = "YOUR_EXTRACTED_GOAL_ID_HERE"
$reviewerId = "00000000-0000-0000-0000-000000000001"

$body = @{
    status = "rejected"
    reviewer_id = $reviewerId
    note = "Rejected - needs more detail"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/extracted-goals/$goalId/decision" `
  -ContentType "application/json" `
  -Body $body
```

## Notes

- All UUIDs should be valid UUID format
- Status values must be one of: `suggested`, `approved`, `rejected`, `created`
- When status is set to `approved` or `rejected`, `decided_at` is automatically set to current time if not provided
- When `goal_text` is updated, `normalized_text` is automatically updated
- `normalized_text` cannot be empty (NOT NULL constraint)
- The `/decision` endpoint automatically sets `decided_at` for approved/rejected statuses


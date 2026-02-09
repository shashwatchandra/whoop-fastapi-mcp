# Cleanup Unused Files Script
# This script archives test files and removes obsolete code files

Write-Host "`n🧹 WHOOP Project Cleanup Script`n" -ForegroundColor Cyan

# Create archive directory
$archiveDir = "archived_tests"
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir | Out-Null
    Write-Host "✓ Created archive directory: $archiveDir" -ForegroundColor Green
}

# Test files to archive
$testFiles = @(
    "test_api_call.py",
    "test_completed_cycles.py",
    "test_date_ranges.py",
    "test_endpoints.py",
    "test_historical_data.py",
    "test_token_path.py",
    "test_token_validity.py",
    "test_v2_api.py",
    "test_whoop_api.py",
    "test_working_endpoints.py",
    "test_yesterday.py",
    "check_data.py",
    "examine_cycle.py"
)

# Archive test files
Write-Host "`n📦 Archiving test files..." -ForegroundColor Yellow
$archivedCount = 0
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Move-Item $file $archiveDir -Force
        Write-Host "  → Moved: $file" -ForegroundColor Gray
        $archivedCount++
    }
}
Write-Host "✓ Archived $archivedCount test files" -ForegroundColor Green

# Files to potentially delete (with confirmation)
$obsoleteFiles = @(
    "simple_app.py",
    "SIMPLE_README.md"
)

Write-Host "`n🗑️  Obsolete files found:" -ForegroundColor Yellow
$deleteCount = 0
foreach ($file in $obsoleteFiles) {
    if (Test-Path $file) {
        Write-Host "  • $file" -ForegroundColor Gray
        $deleteCount++
    }
}

if ($deleteCount -gt 0) {
    $response = Read-Host "`nDelete these obsolete files? (y/n)"
    if ($response -eq 'y') {
        foreach ($file in $obsoleteFiles) {
            if (Test-Path $file) {
                Remove-Item $file -Force
                Write-Host "  ✓ Deleted: $file" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  ⊗ Kept obsolete files" -ForegroundColor Yellow
    }
}

# Check app/ directory
if (Test-Path "app/main.py") {
    Write-Host "`n📁 app/ directory found" -ForegroundColor Yellow
    Write-Host "  Contains alternative FastAPI structure" -ForegroundColor Gray
    $response = Read-Host "Delete app/ directory? (y/n)"
    if ($response -eq 'y') {
        Remove-Item -Recurse -Force app/
        Write-Host "  ✓ Deleted app/ directory" -ForegroundColor Red
    } else {
        Write-Host "  ⊗ Kept app/ directory" -ForegroundColor Yellow
    }
}

# Update .gitignore to exclude archived_tests
Write-Host "`n📝 Updating .gitignore..." -ForegroundColor Yellow
$gitignoreContent = Get-Content .gitignore -Raw
if ($gitignoreContent -notmatch "archived_tests/") {
    Add-Content .gitignore "`n# Archived test files`narchived_tests/"
    Write-Host "  ✓ Added archived_tests/ to .gitignore" -ForegroundColor Green
} else {
    Write-Host "  • archived_tests/ already in .gitignore" -ForegroundColor Gray
}

# Summary
Write-Host "`n✨ Cleanup Complete!" -ForegroundColor Cyan
Write-Host "`nProject structure is now cleaner:" -ForegroundColor White
Write-Host "  ✓ Test files archived in $archiveDir/" -ForegroundColor Green
Write-Host "  ✓ Core application files intact" -ForegroundColor Green
Write-Host "  ✓ Documentation preserved" -ForegroundColor Green

Write-Host "`n📋 Active Files:" -ForegroundColor Cyan
Write-Host "  • whoop_simple.py (FastAPI OAuth server)" -ForegroundColor White
Write-Host "  • whoop_mcp_server.py (MCP server)" -ForegroundColor White
Write-Host "  • test_mcp_server.py (MCP testing - kept)" -ForegroundColor White
Write-Host "  • test_mcp_client.py (MCP testing - kept)" -ForegroundColor White

Write-Host "`n"

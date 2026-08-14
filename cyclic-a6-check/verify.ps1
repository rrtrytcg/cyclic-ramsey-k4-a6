param(
    [switch]$FullProof
)

$ErrorActionPreference = "Stop"
$CheckRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $CheckRoot
$Python = Join-Path $RepoRoot ".local-tools\venv\Scripts\python.exe"
$DratTrim = Join-Path $RepoRoot ".local-tools\drat-trim.exe"
$Proof = Join-Path $CheckRoot "artifacts\proofs\combined_selectors_first_exactly_one.ascii.drat"
$Combined = Join-Path $CheckRoot "artifacts\base\combined_selectors_first_exactly_one.cnf"

function Assert-Hash {
    param([string]$Path, [string]$Expected)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing required artifact: $Path"
    }
    $Actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected) {
        throw "SHA-256 mismatch for ${Path}: expected $Expected, got $Actual"
    }
    Write-Host "hash OK: $Path"
}

if (-not (Test-Path -LiteralPath $Python)) {
    $Python = (Get-Command python -ErrorAction Stop).Source
}

Push-Location $CheckRoot
try {
    & $Python -m unittest -v test_pipeline.py
    if ($LASTEXITCODE -ne 0) { throw "Test suite failed" }

    & $Python compare_cnf.py artifacts/base/authors_base_raw.cnf artifacts/base/independent_base_raw.cnf
    if ($LASTEXITCODE -ne 0) { throw "Independent CNF comparison failed" }

    & $Python audit_combined.py $Combined
    if ($LASTEXITCODE -ne 0) { throw "Combined-CNF audit failed" }

    & $Python validate_model.py --graph6 ..\parsed_graphs\k_palt_cyc\k04_palt06_cyc_15.g6 --require-valid
    if ($LASTEXITCODE -ne 0) { throw "Archived witness validation failed" }

    Assert-Hash $Combined "f59fda6c63246901b7d43f35bcca4adcbb61efff0f09cfce9b44d5b1cdd9da03"
    Assert-Hash (Join-Path $CheckRoot "artifacts\results_91_portfolio.json") "7fe7bbd9744105ea9f9dced36866297f836924eb1cba400f962cd03ba3cf496f"

    if ($FullProof) {
        if (-not (Test-Path -LiteralPath $DratTrim)) {
            throw "Missing proof checker: $DratTrim"
        }
        Assert-Hash $DratTrim "870d6050492744a35354da07e7b2efab5d5caabe41c08597dc39927ef6a78e45"
        Assert-Hash $Proof "38a4f3ffabca676a8e1f77d090db8fadaa92d8328ee4061bf5cc55fbfc877d78"
        & $DratTrim $Combined $Proof
        if ($LASTEXITCODE -ne 0) { throw "DRAT verification failed" }
    }

    Write-Host "All requested verification checks passed."
}
finally {
    Pop-Location
}


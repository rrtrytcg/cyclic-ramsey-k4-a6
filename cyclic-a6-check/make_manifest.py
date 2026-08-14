#!/usr/bin/env python3
"""Hash the publication-critical sources, formulas, result, proof, and tools."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path


def file_record(path: Path, root: Path) -> dict[str, object]:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    try:
        label = str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        label = str(path.resolve()).replace("\\", "/")
    return {"path": label, "bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(".."))
    parser.add_argument("--output", type=Path, default=Path("artifacts/manifest.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    check = Path(__file__).resolve().parent
    paths = [
        root / "src/sat_solving/cnf_generator.cpp",
        root / "include/generators.hpp",
        check / "README.md",
        check / "CITATION.cff",
        check / ".zenodo.json",
        check / "RELEASE_CHECKLIST.md",
        check / "verify.ps1",
        check / "cyclic_a6.py",
        check / "independent_encoder.py",
        check / "combined_encoder.py",
        check / "audit_combined.py",
        check / "test_pipeline.py",
        check / "paper/main.tex",
        check / "paper/main.pdf",
        check / "artifacts/base/authors_base_raw.cnf",
        check / "artifacts/base/independent_base_raw.cnf",
        check / "artifacts/base/combined_selectors_first_exactly_one.cnf",
        check / "artifacts/results_91_portfolio.json",
        check / "artifacts/combined_audit.json",
        check / "artifacts/proofs/combined_selectors_first_exactly_one.ascii.drat",
        check / "artifacts/logs/proof_checks/combined_ascii_drat_trim.log",
        root / "kissat_output/k_palt_cyc/k04_palt06_cyc_15.txt",
        root / "parsed_graphs/k_palt_cyc/k04_palt06_cyc_15.g6",
        root / ".local-tools/kissat-4.0.4-win64.exe",
        root / ".local-tools/drat-trim.exe",
        root / ".local-tools/authors-cnf-generator.exe",
    ]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise SystemExit("missing manifest inputs:\n" + "\n".join(missing))
    manifest = {
        "schema_version": 2,
        "release_version": "1.0.0-rc2",
        "release_date": "2026-08-14",
        "upstream_repository": "https://github.com/Ivan-Damnjanovic/ord-ram-num",
        "upstream_commit": "8ce4e0ab01f1321cb9555703cd8def4d7a1c8511",
        "files": [file_record(path, root) for path in paths],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

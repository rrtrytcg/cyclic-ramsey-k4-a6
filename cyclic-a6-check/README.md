# A certified computation of `R_cyc(K4, P6^alt) = 16`

Final release: **v1.0.0**. The archival certificate package is preserved on
[Zenodo](https://doi.org/10.5281/zenodo.21934069), and the source and smaller
artifacts are released from the companion [GitHub repository](https://github.com/rrtrytcg/cyclic-ramsey-k4-a6).
The manuscript preprint is also deposited in HAL as
[hal-05718992v1](https://hal.science/hal-05718992v1) (currently awaiting
moderation).

This directory contains a reproducible computer-assisted proof that

\[
R_{\mathrm{cyc}}(K_4,P_6^{\mathrm{alt}})=16.
\]

Here `P6^alt` is the alternating ordered path with traversal
`0,5,1,4,2,3`, and cyclic copies preserve orientation: rotations are
allowed and reflections are not.

## Proof at a glance

Use one Boolean variable for each edge of `K15`, with positive meaning blue.
The base CNF forbids red `K4`s and blue cyclic `P6^alt`s. A graph is a
disjoint union of cliques exactly when it has no induced `P3`. After rotating
the unique center of an induced blue `P3` to vertex 0, its two endpoints are
one of the `C(14,2) = 91` pairs `{u,w}`.

The certified CNF selects one such pair and forces

```text
BLUE(0,u), BLUE(0,w), RED(u,w).
```

It is UNSAT. Therefore every valid 15-vertex blue graph is a union of
cliques. It has at most three components (otherwise a red `K4`) and every
component has at most five vertices (otherwise a blue cyclic `P6^alt`). On
15 vertices it is consequently `3K5`.

Now suppose a valid coloring existed on 16 vertices and delete a vertex `x`.
The remaining blue graph is `3K5`. If `x` has a red neighbor in each part,
those three vertices together with `x` form a red `K4`; hence `x` is
blue-complete to one part, producing a blue `K6` and thus a cyclic
`P6^alt`. This contradiction proves the upper bound. The usual `3K5`
coloring supplies the 15-vertex lower-bound example.

## Certified artifact

The accepted certificate is the ASCII DRAT proof. Binary proof attempts are
not used; on Windows, text-mode binary I/O made those files invalid, and they
are quarantined under `artifacts/rejected/`.

| Artifact | Size / result | SHA-256 |
|---|---:|---|
| `artifacts/base/combined_selectors_first_exactly_one.cnf` | 196 variables, 39,859 clauses | `f59fda6c63246901b7d43f35bcca4adcbb61efff0f09cfce9b44d5b1cdd9da03` |
| `artifacts/proofs/combined_selectors_first_exactly_one.ascii.drat` | 817,727,304 bytes | `38a4f3ffabca676a8e1f77d090db8fadaa92d8328ee4061bf5cc55fbfc877d78` |
| `artifacts/logs/proof_checks/combined_ascii_drat_trim.log` | `s VERIFIED` | `ba4f644246ef538f92745866bb366fd105086d3d24c400de6513af71d4a2c887` |

`drat-trim` found an empty clause and verified the proof using 123,107,659
resolution steps. The complete file inventory and hashes are in
`artifacts/manifest.json`.

The release DOI is [10.5281/zenodo.21934069](https://doi.org/10.5281/zenodo.21934069).

The proof is intentionally ignored by Git because it is about 818 MB. It is
present in this working copy and should be deposited as a release asset or in
an archival data repository when the note is submitted.

## Independent checks

The original authors' unmodified C++ generator and the independent Python
encoder produce exactly the same canonical clause multiset:

- 105 edge variables;
- 35,490 raw clauses;
- 16,380 distinct canonical clauses.

The archived 15-vertex model and graph6 file agree. The independent validator
finds three blue `K5` components, no red `K4`, and no blue cyclic
`P6^alt`. All 91 separately forced cases were also solved UNSAT; their
machine-readable record is `artifacts/results_91_portfolio.json`.

## Verification

From this directory, run the fast audit:

```powershell
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

To hash and independently recheck the 818 MB DRAT certificate as well (several
minutes on the reference machine):

```powershell
powershell -ExecutionPolicy Bypass -File .\verify.ps1 -FullProof
```

The script checks hashes before running the proof checker. Local executables
live in the repository-level `.local-tools/` directory and are excluded from
Git. The solver used for the accepted proof is the maintained Windows Kissat
release tagged 4.0.4; its embedded upstream version string reports Kissat
4.0.0. The distinction is recorded rather than normalized away.

## Contents

- `paper/main.tex` and `paper/main.pdf` — submission-style short note by
  Julien Menet, including a detailed contribution statement crediting
  GPT-5.6-SOL and Qwen3.8max with most of the subsequent work after Menet's
  originating structural suggestion.
- `cyclic_a6.py` — independent definitions, encoder, and validators.
- `independent_encoder.py` — standalone base-CNF generator.
- `compare_cnf.py` — canonical clause-set and multiset comparison.
- `combined_encoder.py` — selector encoding for an induced blue `P3`.
- `audit_combined.py` — independent reconstruction of the combined CNF.
- `test_pipeline.py` — unit and end-to-end invariant tests.
- `artifacts/manifest.json` — immutable hashes for the proof package.

The parent repository is the supplementary-code repository of Ba\v{s}i\'c,
Damnjanovi\'c, Stevanovi\'c, and Sto\v{s}i\'c, checked out at commit
`8ce4e0ab01f1321cb9555703cd8def4d7a1c8511`. Our work is confined to this
subdirectory; upstream source files were not modified.

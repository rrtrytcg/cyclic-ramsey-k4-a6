# Publication release checklist

## Review candidate `v1.0.0-rc2`

- [x] Authors' unmodified generator cross-checked against an independent encoder.
- [x] Archived 15-vertex witness independently validated as `3K5`.
- [x] All 91 induced-blue-`P3` cases solved UNSAT.
- [x] Combined CNF reconstructed independently and audited exactly.
- [x] ASCII DRAT certificate independently verified by `drat-trim`.
- [x] Manifest generated with artifact and tool hashes.
- [x] Manuscript compiled and visually inspected.
- [x] AI contribution statement included.
- [ ] Create an isolated private GitHub repository for the review candidate.
- [ ] Send the frozen manuscript privately to the April-paper corresponding author.
- [ ] Record the review deadline and incorporate only substantive corrections.

## Final release `v1.0.0`

- [ ] Re-run `verify.ps1 -FullProof` after the last correction.
- [ ] Compile and visually inspect the final PDF.
- [ ] Regenerate `artifacts/manifest.json` and release checksums.
- [ ] Commit and create an immutable annotated `v1.0.0` tag.
- [ ] Create the GitHub release with source, paper, manifest, CNF, and checker log.
- [ ] Upload the full DRAT package to a Zenodo draft and reserve its DOI.
- [ ] Add the reserved Zenodo DOI to the manuscript and repository README.
- [ ] Publish the Zenodo record and verify every download and checksum.
- [ ] Submit the LaTeX source package to arXiv and approve its compiled preview.
- [ ] Add the arXiv identifier to GitHub and Zenodo metadata.
- [ ] Submit the result to VibeMathed using the arXiv page as the primary source.

Published tags and Zenodo file sets must never be rewritten. Corrections after
publication receive a new semantic version and a new Zenodo version DOI.

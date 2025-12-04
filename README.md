# DSAO: DPV-Aligned Data Sharing Agreement Ontology  
_Explainable-by-Design Validation with SHACL + Human-in-the-Loop (HITL)_

> Reproducible artifact for the ESWC 2026 paper: general-purpose DSA ontology (DPV-aligned), structural SHACL validation, and HITL review logic, evaluated on a **fully synthetic** corpus (100 TTL DSAs; Iter-0 / Iter-1).

---

## 1) Overview

This repository contains:

- **Ontology**: `ontology/dsao.ttl` (core DSAO classes/properties; DPV alignment).
- **SHACL profiles**: `shapes/dsao-shapes-structural.ttl` (must-level constraints for Table 2).
- **Synthetic corpora**  
  - **Iter-0** (baseline): `dsao_synth_from_overview/iter_0/instances/*.ttl`  
    + `iter_0/manifest_gold_hitl.csv` (gold defects + HITL outcomes)
  - **Iter-1** (fixed + hints): `dsao_synth_from_overview/iter_1_fix/instances/*.ttl`  
    + `iter_1_fix/manifest_iter1_fix.csv`
- **Evaluation scripts** (Tables 2–4): under `src/` (Python).
- **Explainable-by-design pipeline**: every result is traceable to (requirement → pattern → SHACL shape → CQ → reviewer/hint).

> ⚠️ The corpus is **synthetic** on purpose to allow controlled, repeatable experiments without exposing real DSAs.

---

## 2) Directory Layout

```
.
├─ ontology/
│  └─ dsao.ttl
├─ shapes/
│  └─ dsao-shapes-structural.ttl
├─ dsao_synth_from_overview/
│  ├─ iter_0/
│  │  ├─ instances/            # 100 TTL DSAs (gold defects + reviewer outcomes)
│  │  └─ manifest_gold_hitl.csv
│  └─ iter_1_fix/
│     ├─ instances/            # 100 TTL DSAs (all structural fixes + hint flags)
│     └─ manifest_iter1_fix.csv
├─ queries/
│  ├─ CQ1_pa_purpose_legalbasis.sparql
│  ├─ CQ2_dataset_retention_disposal.sparql
│  ├─ CQ3_transfer_mechanism_safeguard.sparql
│  └─ CQ4_pa_datacategories.sparql
├─ src/
│  ├─ eval_table2.py           # SHACL structural detection (D1–D3 + micro-avg)
│  ├─ eval_cq_coverage.py      # CQ Answerability Coverage (Table 3)
│  └─ eval_hgain.py            # HITL H-Gain (Table 4)
└─ results/                    # (created on first run)
```

---

## 3) Prerequisites

- Python ≥ 3.9
- Install dependencies:
  ```bash
  python -m pip install rdflib pyshacl pandas tabulate
  ```
- (Optional) Java/Jena for alternative validation, but **not required**.

---

## 4) Quick Start (All Tables in ~5 Minutes)

```bash
# 1) Validate Iter-0 with structural SHACL (produce reports)
mkdir -p reports/iter0 reports/iter1
for f in dsao_synth_from_overview/iter_0/instances/*.ttl; do
  b=$(basename "$f" .ttl)
  pyshacl -s shapes/dsao-shapes-structural.ttl -m -i rdfs -f turtle     -o reports/iter0/${b}_report.ttl "$f"
done

# 2) Validate Iter-1 (sanity: structural defects should be cleared)
for f in dsao_synth_from_overview/iter_1_fix/instances/*.ttl; do
  b=$(basename "$f" .ttl)
  pyshacl -s shapes/dsao-shapes-structural.ttl -m -i rdfs -f turtle     -o reports/iter1/${b}_report.ttl "$f"
done

# 3) Reproduce Table 2 (D1–D3 + micro-average)
python src/eval_table2.py   --iter0-manifest dsao_synth_from_overview/iter_0/manifest_gold_hitl.csv   --iter0-reports reports/iter0   --shape-file shapes/dsao-shapes-structural.ttl   --shape-d1 SH-PA-LB-01 --shape-d2 SH-DS-DISP-01 --shape-d3 SH-XFER-MECH-01

# 4) Reproduce Table 3 (CQ coverage, Iter-0 vs Iter-1)
python src/eval_cq_coverage.py   --corpus dsao_synth_from_overview/iter_0/instances --label Iter-0   --out-csv results/cq_coverage_iter0.csv
python src/eval_cq_coverage.py   --corpus dsao_synth_from_overview/iter_1_fix/instances --label Iter-1   --out-csv results/cq_coverage_iter1.csv

# 5) Reproduce Table 4 (H-Gain from hints on prior manual flags)
python src/eval_hgain.py   --iter0-manifest dsao_synth_from_overview/iter_0/manifest_gold_hitl.csv   --iter1-dir dsao_synth_from_overview/iter_1_fix/instances
```

---

## 5) What Each Table Measures

- **Table 2 – Structural Defects (D1–D3)**  
  SHACL **must-level** violations against gold-labeled defects in Iter-0:  
  - D1: missing `dpv:hasLegalBasis` on `dsao:ProcessingActivity` (`SH-PA-LB-01`)  
  - D2: missing `dsao:disposalMethod` on `dsao:SharedDataset` (`SH-DS-DISP-01`)  
  - D3: missing `dsao:transferMechanism` on `dsao:InternationalTransfer` (`SH-XFER-MECH-01`)  
  We compute **Precision/Recall/F1** (micro-average over D1–D3).

- **Table 3 – CQ Answerability Coverage**  
  Proportion of DSAs for which each CQ returns ≥1 row with **all required variables bound**.  
  CQs are in `queries/` and cover: purpose+legal basis, retention+disposal, transfers+mechanisms+safeguards, and PD categories.

- **Table 4 – HITL H-Gain**  
  From **Iter-0** gold manual flags (`manifest_gold_hitl.csv`) to **Iter-1** hint pre-screens (`dsao:hintFired "true"` in `dsao:ReviewNote`):  
  \[
    \mathrm{H	ext{-}Gain}_c = rac{M_c}{N_c}
  \]
  where \(N_c\) = # prior manual flags, \(M_c\) = # now pre-screened by hints.  
  Categories: **proportionality** and **safeguards adequacy**.

---

## 6) Explainable-by-Design (Traceability)

We treat explainability as a design constraint:

- **Requirement → Pattern → Shape → CQ → Reviewer/Hint**  
- Every run leaves **artifacts**: SHACL reports, CQ result logs, and ReviewNote annotations.  
- A reviewer can trace a number in a table to the **concrete constraint** that fired, the **query** that (failed to) bind variables, and the **review/hint** that drove shape evolution.

---

## 7) Troubleshooting

- **All CQ coverages = 0.00**  
  - Check you pointed to the right folder: use `iter_1_fix/instances/` (not a malformed archive).  
  - Parse one file manually:
    ```python
    from rdflib import Graph
    g = Graph(); g.parse("dsao_synth_from_overview/iter_0/instances/dsa_070.ttl", format="turtle")
    print(len(g))
    ```
  - Ensure the SPARQL prefixes match the data:
    `dsao: <https://w3id.org/dsao#>` and `dpv: <https://w3id.org/dpv#>`.

- **SHACL reports empty**  
  - Use `-i rdfs` in `pyshacl` to activate RDFS typing if needed.

- **H-Gain does not match**  
  - Verify Iter-1 files contain `dsao:hintFired "true"` on the expected `dsao:ReviewNote` nodes.  
  - Confirm `manifest_gold_hitl.csv` is intact (20 proportionality, 20 safeguards manual flags).

---

## 8) Citing

If you use this artifact, please cite the paper (ESWC 2026) and the DSAO repository.  
Key background references for ontology/validation metrics:

- Brank, J., Grobelnik, M., & Mladenić, D. (2005). *A survey of ontology evaluation techniques.*  
- Gómez-Pérez, A. (2004). *Ontological Engineering.*  
- W3C (2017). *SHACL — Shapes Constraint Language (Recommendation).*  
- Powers, D. M. W. (2011). *Evaluation: From precision, recall and F-measure…*  
- Zaveri, A., et al. (2016). *Quality assessment for Linked Data.* Semantic Web, 7(1), 63–93.

---

## 9) License

- **Ontology & shapes**: CC-BY 4.0  
- **Synthetic corpora & scripts**: MIT

---

## 10) Maintainers & Contributions

PRs welcome! Please:
1. Keep new shapes in **separate profiles** (avoid contaminating Table 2 runs).
2. Add tests and a minimal example if you introduce new CQs.
3. Preserve **traceability** (IDs, logs) so results remain explainable and reproducible.

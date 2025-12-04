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
- **Evaluation scripts**: under `src/` (Python).

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

## 4) What Each Table Measures

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

## 5) License

- **Ontology & shapes**: CC-BY 4.0  
- **Synthetic corpora & scripts**: MIT

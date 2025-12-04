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
   ├─ CQ1_pa_purpose_legalbasis.sparql
   ├─ CQ2_dataset_retention_disposal.sparql
   ├─ CQ3_transfer_mechanism_safeguard.sparql
   └─ CQ4_pa_datacategories.sparql
```
---

## 3) License

- **Ontology & shapes**: CC-BY 4.0  
- **Synthetic corpora & scripts**: MIT

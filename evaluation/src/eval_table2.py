#!/usr/bin/env python3
import argparse, pathlib, pandas as pd
from rdflib import Graph, Namespace, URIRef

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter0-manifest", required=True)
    ap.add_argument("--iter0-reports", required=True)
    ap.add_argument("--shape-file", required=False, help="Not parsed; only for bookkeeping")
    # Allow custom shape IRIs/labels if needed
    ap.add_argument("--shape-d1", default="SH-PA-LB-01")
    ap.add_argument("--shape-d2", default="SH-DS-DISP-01")
    ap.add_argument("--shape-d3", default="SH-XFER-MECH-01")
    args = ap.parse_args()

    man = pd.read_csv(args.iter0_manifest)
    man["filebase"] = man["filename"].str.replace(".ttl","", regex=False)

    # Map defect → shape ID
    DEFECTS = {
        "D1": args.shape_d1,
        "D2": args.shape_d2,
        "D3": args.shape_d3,
    }
    # Columns in manifest → defects
    GOLD_COL = {
        "D1": "D1_missing_legal_basis",
        "D2": "D2_missing_disposal_method",
        "D3": "D3_missing_transfer_mechanism",
    }

    # Parse SHACL reports: does a result exist from the given shape?
    SH = Namespace("http://www.w3.org/ns/shacl#")

    def predicted_positive(report_path: pathlib.Path, shape_id: str) -> bool:
        g = Graph()
        print(report_path)
        g.parse(report_path.as_posix(), format="turtle")
        # Find any sh:ValidationResult with this sh:sourceShape (IRI or literal label)
        
        for r in g.subjects(SH.sourceShape, None):
            
            # Often sourceShape is a blank node or an IRI; we compare string contains
            # against the shape_id to be robust to full IRIs or IDs in labels/messages.
            val = str(list(g.objects(r, SH.sourceShape))[0])
            if shape_id in val:
                print("entro")
                return True
        # Fallback: check message carries the identifier
        for m in g.objects(None, SH.resultMessage):
            print(shape_id)
            print(str(m))
            if shape_id in str(m):
                print("Entro aqui")
                return True
        return False

    rows = []
    reports_dir = pathlib.Path(args.iter0_reports)
    for _, r in man.iterrows():
        fb = r["filebase"]
        report = reports_dir / f"{fb}_report.ttl"
        if not report.exists():
            raise SystemExit(f"Missing SHACL report for {fb}: {report}")
        for d, shape_id in DEFECTS.items():
            gold = bool(r[GOLD_COL[d]])
            pred = predicted_positive(report, shape_id)
            rows.append({"filebase": fb, "defect": d, "gold": gold, "pred": pred})

    df = pd.DataFrame(rows)

    def prf(sub):
        tp = ((sub.gold == True) & (sub.pred == True)).sum()
        fp = ((sub.gold == False) & (sub.pred == True)).sum()
        fn = ((sub.gold == True) & (sub.pred == False)).sum()
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec  = tp / (tp + fn) if (tp + fn) else 0.0
        f1   = (2*prec*rec / (prec+rec)) if (prec+rec) else 0.0
        return tp, fp, fn, prec, rec, f1

    # Per-category
    out_rows = []
    for d in ["D1","D2","D3"]:
        sub = df[df.defect == d]
        tp, fp, fn, p, r, f1 = prf(sub)
        out_rows.append([d, int(tp+fn), int(tp), int(fp), int(fn),
                         f"{p:.3f}", f"{r:.3f}", f"{f1:.3f}"])

    # Micro-average
    tp, fp, fn, p, r, f1 = prf(df)
    out_rows.append(["Overall (micro)", int(tp+fn), int(tp), int(fp), int(fn),
                     f"{p:.3f}", f"{r:.3f}", f"{f1:.3f}"])

    # Print Table 2 replica
    print("\nTable 2 — SHACL structural defect detection (Iter-0)")
    print("Defect\tGold(+)\tTP\tFP\tFN\tPrecision\tRecall\tF1")
    for row in out_rows:
        print("\t".join(map(str,row)))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse, pathlib, sys
from rdflib import Graph
import pandas as pd
from tabulate import tabulate

CQS = [
    ("CQ1", "queries/CQ1_pa_purpose_legalbasis.sparql",
     ["pa", "purpose", "lb"]),
    ("CQ2", "queries/CQ2_dataset_retention_disposal.sparql",
     ["dataset", "duration", "disposal"]),
    ("CQ3", "queries/CQ3_transfer_mechanism_safeguard.sparql",
     ["transfer", "dest", "mechanism", "safeguard"]),
    ("CQ4", "queries/CQ4_pa_datacategories.sparql",
     ["pa", "pdCat"]),
]

def run_query(g: Graph, qpath: pathlib.Path):
    q = qpath.read_text(encoding="utf-8")

    #print(g)
    rows = []
    
    for b in g.query(q):
        #print("entro -->" + b)
        # Convert to dict with str() for determinism
        rows.append({str(v): (str(b[v]) if b[v] is not None else None) for v in b.labels})
    #print(rows)
    return rows, q

def covered(rows, required_vars):
    if not rows:
        return False
    # At least one row and all required vars bound in every row? We require: at least one row with ALL vars bound.
    for r in rows:
        if all((v in r) and (r[v] is not None) and (r[v] != "") for v in required_vars):
            return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, help="Path to folder with TTLs")
    ap.add_argument("--label", required=True, help="Label for this run, e.g., Iter-0 or Iter-1")
    ap.add_argument("--out-csv", default=None)
    args = ap.parse_args()

    base = pathlib.Path(args.corpus)
    files = sorted(base.glob("*.ttl"))
    if not files:
        print(f"No TTL files in {base}", file=sys.stderr); sys.exit(2)

    per_doc = []
    for f in files:
        g = Graph()
        g.parse(f.as_posix(), format="turtle")
        for cq_id, cq_path, req_vars in CQS:
            rows, qtxt = run_query(g, pathlib.Path(cq_path))
            is_cov = covered(rows, req_vars)
            per_doc.append({
                "doc": f.name,
                "cq": cq_id,
                "covered": int(is_cov),
                "rows": len(rows),
                "required_vars": ",".join(req_vars),
                "query_path": cq_path,
            })

    df = pd.DataFrame(per_doc)
    summary = (df.groupby("cq")["covered"].mean()
                 .reindex([c[0] for c in CQS])
                 .rename(args.label)).reset_index()
    print(tabulate(summary, headers="keys", tablefmt="github", floatfmt=".2f"))

    if args.out_csv:
        out = pathlib.Path(args.out_csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        # Write both per-doc logs and the summary
        df.to_csv(out.with_suffix(".details.csv"), index=False)
        summary.to_csv(out, index=False)

if __name__ == "__main__":
    main()

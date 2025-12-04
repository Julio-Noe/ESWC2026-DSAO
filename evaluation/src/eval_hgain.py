#!/usr/bin/env python3
import argparse, pathlib
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal

DSAO = Namespace("https://example.org/dsao#")

def has_hint_fired(ttl_path: pathlib.Path, reviewnote_local: str) -> bool:
    
    g = Graph()
    g.parse(ttl_path.as_posix(), format="turtle")
    # RN is a relative :caseX_RN_... in data; rdflib will treat it as a QName only with a base.
    # Robust approach: search by ReviewNote type + localname match + hintFired true.
    for s in g.subjects(predicate=None, object=DSAO.ReviewNote):
        pass
    # Fallback: iterate all ReviewNotes and match by string containment on N-Triples
    for s in g.subjects(None, None):
        # Quickly filter only ReviewNotes
        if (s, None, None) not in g:
            continue
        if (s, None, DSAO.ReviewNote) in g or (s, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), DSAO.ReviewNote) in g:
            if reviewnote_local in str(s):
                # Check dsao:hintFired "true"
                for lit in g.objects(s, DSAO.hintFired):
                    if str(lit).lower() == "true":
                        return True
    # Also check by generic scan if localname couldn't be matched as node IRI
    for s in g.subjects(None, None):
        if reviewnote_local in str(s):
            for lit in g.objects(s, DSAO.hintFired):
                if str(lit).lower() == "true":
                    return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter0-manifest", required=True)
    ap.add_argument("--iter1-dir", required=True)
    args = ap.parse_args()

    man = pd.read_csv(args.iter0_manifest)
    man["filebase"] = man["filename"].str.replace(".ttl","", regex=False)



    # Build gold sets N_c from Iter-0 manifest
    prop_gold = man[man["HITL_proportionality"] == "needs-change"]["filebase"].tolist()
    saf_gold  = man[man["HITL_safeguards_adequacy"] == "needs-change"]["filebase"].tolist()

    # Count M_c in Iter-1 by checking dsao:hintFired on the respective ReviewNotes
    iter1 = pathlib.Path(args.iter1_dir)

    def count_prescreen(gold_list, rn_suffix):
        M = 0
        checked = []
        for fb in gold_list:
            ttl = iter1 / f"{fb}.ttl"
            #rn_local = f"{fb}_RN_{rn_suffix}"   # e.g., case12_RN_proportionality
            rn_local = f"RN_{rn_suffix}"   # e.g., case12_RN_proportionality
            if has_hint_fired(ttl, rn_local):
                M += 1
            checked.append((fb, rn_local))
        return M, len(gold_list), checked

    M_prop, N_prop, _ = count_prescreen(prop_gold, "proportionality")
    M_saf,  N_saf,  _ = count_prescreen(saf_gold,  "safeguards")

    # Compute H-Gain
    h_prop = (M_prop / N_prop) if N_prop else 0.0
    h_saf  = (M_saf  / N_saf)  if N_saf  else 0.0
    macro  = (h_prop + h_saf) / 2 if (N_prop and N_saf) else 0.0

    print("\nTable 4 — HITL coverage by hints (H-Gain)")
    print(f"Category\tN_c\tM_c\tH-Gain")
    print(f"Proportionality\t{N_prop}\t{M_prop}\t{h_prop:.2f}")
    print(f"Safeguards\t{N_saf}\t{M_saf}\t{h_saf:.2f}")
    print(f"Macro-average\t-\t-\t{macro:.2f}")

if __name__ == "__main__":
    main()

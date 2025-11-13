#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate DSA TTL files from a table (CSV) using rdflib.

Usage:
  python generate_dsa_ttl.py --csv input.csv --out out_dir --base https://fid.example.org
RUN
  /Users/juliohernandez/Julio/work/DCU/Fidelity/git/Privacy-Policy-Agreement-Ontology/csv2rdf/venv/bin/python /Users/juliohernandez/Julio/work/DCU/Fidelity/git/Privacy-Policy-Agreement-Ontology/csv2rdf/fillTemplate.py --csv ./template_synthetic.csv --out /Users/juliohernandez/Julio/work/DCU/Fidelity/git/Privacy-Policy-Agreement-Ontology/csv2rdf/synthetic_V02

Notes:
- Cells that are IRIs should start with http(s):// OR use known prefixes like dpv:, schema:, fid:
- Dates must be ISO format (YYYY-MM-DD)
- Booleans must be 'true' or 'false'
"""

import argparse
import csv
import os
from pathlib import Path
from typing import Optional

from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, XSD, NamespaceManager

# --- Namespaces ---
DPV    = Namespace("https://w3id.org/dpv#")
FID    = Namespace("http://fid.example.org/ontologies/fid/")
SCHEMA = Namespace("http://schema.org/")
DCT    = Namespace("http://purl.org/dc/terms/")

# allow compact "dpv:Something" etc.
PREFIXES = {
    "dpv": DPV,
    "fid": FID,
    "schema": SCHEMA,
    "dct": DCT,
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
}

def bind_prefixes(g: Graph):
    nm = NamespaceManager(g)
    for p, ns in PREFIXES.items():
        nm.bind(p, ns)
    g.namespace_manager = nm

def is_iri(val: str) -> bool:
    return val.startswith("http://") or val.startswith("https://") or val.startswith("mailto:")

def qname_to_uri(val: str) -> Optional[URIRef]:
    """Turn 'dpv:Analytics' into the full URIRef, if prefix is known."""
    if ":" not in val:
        return None
    prefix, local = val.split(":", 1)
    ns = PREFIXES.get(prefix)
    if ns is None or not local:
        return None
    return ns[local]

def as_uri_or_literal(val: str, datatype: Optional[URIRef] = None) -> URIRef | Literal:
    """Return URIRef if value looks like IRI or known QName, else xsd-typed or plain literal."""
    val = val.strip()
    if not val:
        return Literal("")  # or raise; keeping empty literal is safer for bulk loads
    if is_iri(val):
        return URIRef(val)
    q = qname_to_uri(val)
    if q:
        return q
    return Literal(val, datatype=datatype) if datatype else Literal(val)

def add_person(g: Graph, uri:URIRef, literal: Literal):
    """Create a minimal schema:Person with a readable name derived from last path segment."""
    if not isinstance(uri, URIRef):
        return
    #label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, SCHEMA.Person))
    g.add((uri, SCHEMA.name, Literal(literal)))

def add_auc(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, FID.AUC))
    g.add((uri, DCT.description, Literal(label)))

def add_lob(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, DPV.LineOfBusiness))
    g.add((uri, DCT.description, Literal(label)))

def add_domain_stub(g: Graph, uri: URIRef, klass: URIRef):
    if not isinstance(uri, URIRef):
        return
    g.add((uri, RDF.type, klass))

def add_contactpoint(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, SCHEMA.ContactPoint))
    g.add((uri, DCT.description, Literal(label)))

def add_dataset(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, FID.DataSet))
    g.add((uri, DCT.description, Literal(label)))

def add_dup(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, DPV.DataUsagePolicy))
    g.add((uri, DCT.description, Literal(label)))

def add_purpose(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, DPV.Purpose))
    g.add((uri, DCT.description, Literal(label)))

def add_retention(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, DPV.StorageDuration))
    g.add((uri, DCT.description, Literal(label)))

def add_subject_area(g: Graph, uri: URIRef):
    if not isinstance(uri, URIRef):
        return
    label = uri.toPython().rstrip("/").split("/")[-1].replace("-", " ").title()
    g.add((uri, RDF.type, FID.SubjectArea))
    g.add((uri, DCT.description, Literal(label)))

def derive_duration_from_id(retention_uri: URIRef) -> Optional[str]:
    """
    Convenience: if your retention IRI ends with RET-3M/RET-6M/... derive an ISO 8601 duration.
    """
    if not isinstance(retention_uri, URIRef):
        return None
    tail = retention_uri.toPython().rstrip("/").split("/")[-1].upper()
    mapping = {
        "RET-3M": "P3M", "RET-6M": "P6M", "RET-9M": "P9M",
        "RET-12M": "P12M", "RET-18M": "P18M", "RET-24M": "P24M",
        "RET-36M": "P36M", "RET-48M": "P48M", "RET-60M": "P60M",
    }
    return mapping.get(tail)

def add_dpv_use(g: Graph, use_uri: URIRef, text: str):
    g.add((use_uri, RDF.type, DPV.Use))
    g.add((use_uri, DCT.description, Literal(text, datatype=XSD.string)))

def build_graph_from_row(row: dict, base: str) -> Graph:
    g = Graph()
    bind_prefixes(g)

    # Subject IRI for the DSA
    dsa_id = row["dsaID"].strip()
    subj = URIRef(f"{base}/dsa/{dsa_id}")

    g.add((subj, RDF.type, DPV.DataSharingAgreement))
    g.add((subj, DCT.title, Literal(row["text_dsa_Title"], lang="en")))

    # --- GovernanceMetadata (blank node) ---
    gm = BNode()
    g.add((subj, FID.hasGovernanceMetadata, gm))
    g.add((gm, RDF.type, FID.GovernanceMetadata))
    g.add((gm, FID.hasSupportingArtifact, Literal(row["text_supporting_artifact"], datatype=XSD.anyURI)))
    g.add((gm, FID.hasCategoryGroup, Literal(row["text_categorygroup"], datatype=XSD.string)))
    g.add((gm, FID.hasComment, Literal(row["text_comment"], datatype=XSD.string)))
    g.add((gm, DCT.description, Literal(row["text_description"], datatype=XSD.string)))

    # --- InvolvedParty (blank node) ---
    ip = BNode()
    g.add((subj, FID.hasInvolvedParty, ip))
    g.add((ip, RDF.type, FID.InvolvedParty))

    cons_approver = as_uri_or_literal(row["reference_consumer_approver"])
    prod_approver = as_uri_or_literal(row["reference_producer_approver"])
    #g.add((ip, FID.hasConsumerApprover, cons_approver))
    #g.add((ip, FID.hasProducerApprover, prod_approver))
    g.add((ip, FID.hasConsumerApprover, FID.consumer_approver))
    g.add((ip, FID.hasProducerApprover, FID.producer_approver))
    # minimally type and label those approvers if they are URIs
    if isinstance(FID.consumer_approver, URIRef): add_person(g, FID.consumer_approver, cons_approver)
    if isinstance(FID.producer_approver, URIRef): add_person(g, FID.producer_approver, prod_approver)

    cons_lob = as_uri_or_literal(row["reference_consumer_LOB"])
    prod_lob = as_uri_or_literal(row["reference_producer_LOB"])
    g.add((ip, FID.hasConsumerBusinessUnit, cons_lob))
    g.add((ip, FID.hasProducerBusinessUnit, prod_lob))
    if isinstance(cons_lob, URIRef): add_lob(g, cons_lob)
    if isinstance(prod_lob, URIRef): add_lob(g, prod_lob)

    # --- TemporalConstraint ---
    tc = BNode()
    g.add((subj, FID.hasTemporalConstraint, tc))
    g.add((tc, RDF.type, FID.TemporalConstraint))
    g.add((tc, FID.hasEffectiveStartDate, Literal(row["effective_start_date"], datatype=XSD.date)))
    g.add((tc, FID.hasEffectiveEndDate,   Literal(row["effective_end_date"],   datatype=XSD.date)))
    g.add((tc, FID.hasLastReviewDate,     Literal(row["last_review_date"],     datatype=XSD.date)))
    g.add((tc, FID.hasNextReviewDate,     Literal(row["next_review_date"],     datatype=XSD.date)))

    # --- GovernanceScope ---
    gs = BNode()
    g.add((subj, FID.hasGovernanceScope, gs))
    g.add((gs, RDF.type, FID.GovernanceScope))
    g.add((gs, FID.coversBusinessTerm, as_uri_or_literal(row["reference_business_term"])))
    # Template used xsd:string; change to boolean if your ontology expects one:
    g.add((gs, FID.coversHighlyConfidentialData, Literal(row["text_covers_highly_confidential_data"], datatype=XSD.string)))
    if ',' in row["reference_subject_area"]:
        content = row["reference_subject_area"]
        for option in content.split(','):
            subject_area = as_uri_or_literal(option)
            g.add((gs, FID.coversSubjectArea, subject_area))
            if isinstance(subject_area,URIRef):
                add_subject_area(g,subject_area)
            #g.add((gs, FID.coversSubjectArea, as_uri_or_literal(option)))
    else:
        subject_area = as_uri_or_literal(row["reference_subject_area"])
        g.add((gs, FID.coversSubjectArea, subject_area))
        if isinstance(subject_area,URIRef):
            add_subject_area(g,subject_area)
        g.add((gs, FID.coversSubjectArea, as_uri_or_literal(row["reference_subject_area"])))
    #g.add((gs, FID.coversSubjectArea, as_uri_or_literal(row["SubjectArea"])))
    if ',' in row["reference_approved_business_use_case"]:
        content = row["reference_approved_business_use_case"]
        for option in content.split(','):
            auc = as_uri_or_literal(option)
            g.add((gs, FID.governsBusinessUseCase, auc))
            if isinstance(auc, URIRef): add_auc(g, auc)
            #g.add((gs, FID.governsBusinessUseCase, as_uri_or_literal(option)))
    else:
        auc = as_uri_or_literal(row["reference_approved_business_use_case"])
        g.add((gs, FID.governsBusinessUseCase, auc))
        if isinstance(auc, URIRef): add_auc(g, auc)
        

    #g.add((gs, FID.governsBusinessUseCase, as_uri_or_literal(row["ApprovedUseCase"])))
    g.add((gs, FID.governsDataMovementAccess, as_uri_or_literal(row["reference_data_movement_access"])))
    dataset = as_uri_or_literal(row["reference_data_set"])
    g.add((gs, FID.coversDataSet, dataset))
    if isinstance(dataset, URIRef): add_dataset(g, dataset)
    #g.add((gs, FID.coversDataSet, as_uri_or_literal(row["reference_data_set"])))
    
    g.add((gs, FID.isRequiredByBusinessDimension, as_uri_or_literal(row["reference_business_dimension"])))
    if ',' in row["reference_data_usage_policy"]:
        content = row["reference_data_usage_policy"]
        for option in content.split(','):
            dup = as_uri_or_literal(content)
            g.add((gs, FID.requiresDataUsagePolicy,dup))
            if isinstance(dup,URIRef):
                add_dup(g,dup)
            #g.add((gs, FID.requiresDataUsagePolicy, as_uri_or_literal(option)))
    else:
        dup = as_uri_or_literal(row["reference_data_usage_policy"])
        g.add((gs, FID.requiresDataUsagePolicy,dup))
        if isinstance(dup,URIRef):
            add_dup(g,dup)
        #g.add((gs, FID.requiresDataUsagePolicy, as_uri_or_literal(row["reference_data_usage_policy"])))   
    #g.add((gs, FID.requiresDataUsagePolicy, as_uri_or_literal(row["dpv:DataUsagePolicy"])))

    # Stubs for the domain resources (optional, but makes files stand-alone)
    for col, klass in [
        ("reference_business_term", FID.BusinessTerm),
        ("reference_subject_area", FID.SubjectArea),
        ("reference_approved_business_use_case", FID.ApprovedUseCase),
        ("reference_data_movement_access", FID.DataMovementAccess),
        ("reference_data_set", DPV.DataSet),
        ("reference_business_dimension", FID.BusinessDimension),
        ("reference_data_usage_policy", DPV.DataUsagePolicy),
    ]:
        if ',' in row[col]:
            content = row[col]
            for option in content.split(','):
                #val = as_uri_or_literal(row[col])
                val = as_uri_or_literal(option)
                if isinstance(val, URIRef): add_domain_stub(g, val, klass)

    # --- UsageControlPolicy ---
    ucp = BNode()
    g.add((subj, FID.hasUsageControlPolicy, ucp))
    g.add((ucp, RDF.type, FID.UsageControlPolicy))

    acceptable_use   = as_uri_or_literal(row["reference_acceptable_use"])
    actual_use       = as_uri_or_literal(row["reference_actual_use"])
    tparty_use       = as_uri_or_literal(row["reference_third_party_use"])
    unacceptable_use = as_uri_or_literal(row["reference_unacceptable_use"])
    g.add((ucp, FID.hasAcceptableUse, acceptable_use))
    g.add((ucp, FID.hasActualUse, actual_use))
    g.add((ucp, FID.hasThirdPartyUseRestriction, tparty_use))
    g.add((ucp, FID.hasUnacceptableUse, unacceptable_use))

    # declared purpose (QName or IRI)
    purpose = as_uri_or_literal(row["reference_purpose"])
    g.add((ucp,FID.hasDeclaredPurpose,purpose))
    if isinstance(purpose,URIRef):
        add_purpose(g,purpose)
    #g.add((ucp, FID.hasDeclaredPurpose, as_uri_or_literal(row["reference_purpose"])))
    g.add((ucp, FID.hasExceptionScenario, Literal(row["literal_exception_scenario"], datatype=XSD.string)))
    g.add((ucp, FID.isThirdPartyUsedAllowed, Literal(row["literal_third_party_use"], datatype=XSD.boolean)))

    # Create dpv:Use nodes with default descriptions if not already in data
    if isinstance(acceptable_use, URIRef):
        add_dpv_use(g, acceptable_use, "Acceptable use (internal/allowed operations).")
    if isinstance(actual_use, URIRef):
        add_dpv_use(g, actual_use, "Actual use (what is being done in practice).")
    if isinstance(tparty_use, URIRef):
        add_dpv_use(g, tparty_use, "Third-party use restriction or allowance.")
    if isinstance(unacceptable_use, URIRef):
        add_dpv_use(g, unacceptable_use, "Unacceptable use (explicitly prohibited).")

    # --- DataLifecycleManagement ---
    dlm = BNode()
    g.add((subj, FID.hasDataLifecycleManagement, dlm))
    g.add((dlm, RDF.type, FID.DataLifecycleManagement))
    g.add((dlm, FID.hasDataPropagation, Literal(row["string_data_propagation"], datatype=XSD.string)))
    issue_iri = as_uri_or_literal(row["reference_issue"])
    g.add((dlm, FID.isImpactedByIssue, issue_iri))
    g.add((dlm, FID.hasDataQualityCondition, Literal(row["literal_data_quality_condition"], datatype=XSD.string)))

    # Retention node (IRI provided)
    retention = as_uri_or_literal(row["reference_storage_duration"])
    g.add((dlm, FID.hasDataRetentionPeriod, retention))
    if isinstance(retention, URIRef):
        add_retention(g,retention)
    # If it's an IRI, also (optionally) define it with dpv:StorageDuration and derived hasDuration
    if isinstance(retention, URIRef):
        g.add((retention, RDF.type, DPV.StorageDuration))
        maybe = derive_duration_from_id(retention)
        if maybe:
            g.add((retention, DPV.hasDuration, Literal(maybe, datatype=XSD.duration)))

    # Issue stub (optional)
    if isinstance(issue_iri, URIRef):
        g.add((issue_iri, RDF.type, FID.Issue))
        g.add((issue_iri, DCT.description, Literal("Tracked issue", lang="en")))

    # --- CommunicationPreference ---
    cp = BNode()
    g.add((subj, FID.hasCommunicationPreference, cp))
    g.add((cp, RDF.type, FID.CommunicationPreference))
    contact = as_uri_or_literal(row["reference_schema_contact_point"])
    g.add((cp, FID.hasPreferredCommunicationChannel, contact))
    # Minimal contact stub
    if isinstance(contact, URIRef):
        add_contactpoint(g,contact)
        #g.add((contact, RDF.type, SCHEMA.ContactPoint))

    # --- AccessControlPolicy ---
    acp = BNode()
    g.add((subj, FID.hasAccessControlPolicy, acp))
    g.add((acp, RDF.type, FID.AccessControlPolicy))
    role = as_uri_or_literal(row["reference_data_lake_access_role"])
    g.add((acp, FID.governsDataLakeAccessRole, role))
    if isinstance(role, URIRef):
        g.add((role, RDF.type, FID.DataLakeAccessRole))

    return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Input CSV file (one row per DSA)")
    ap.add_argument("--out", required=True, help="Output directory for TTL files")
    ap.add_argument("--base", default="https://fid.example.org", help="Base IRI for generating subject IRIs")
    args = ap.parse_args()

    outdir = Path(args.out)
    print("outdir\n\n\n\n",outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    with open(args.csv, newline="", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        # sanity: required headers
        """ required = {
            "dsaID","Title","url","text_categorygroup","text_comment","Description",
            "ConsumerApprover","ProducerApprover","Consumer_LOB","Producer_LOB",
            "effective_start_date","effective_end_date","last_review_date","next_review_date",
            "BusinessTerm","coversHighlyConfidentialData","SubjectArea","ApprovedUseCase",
            "DataMovementAccess","DataSet","BusinessDimension","DataUsagePolicy",
            "Acceptable_use","Actual_use","Third_party_use","Unacceptable_use",
            "dpv_Purpose","literal_exception_scenario","literal_third_party_use",
            "string_data_propagation","Issue","Literal_Data_quality_condition",
            "dpv_storage_duration","schema_contact_point","DataLakeAccessRole"
        } """

        required = {
            "dsaID","text_dsa_Title","text_supporting_artifact","text_categorygroup","text_comment","text_description","reference_consumer_approver",
            "reference_producer_approver","reference_consumer_LOB","reference_producer_LOB","effective_start_date","effective_end_date",
            "last_review_date","next_review_date","reference_business_term","text_covers_highly_confidential_data","reference_subject_area","reference_approved_business_use_case",
            "reference_data_movement_access","reference_data_set","reference_business_dimension","reference_data_usage_policy","reference_acceptable_use",
            "reference_actual_use","reference_third_party_use","reference_unacceptable_use","reference_purpose","literal_exception_scenario",
            "literal_third_party_use","string_data_propagation","reference_issue","literal_data_quality_condition",
            "reference_storage_duration","reference_schema_contact_point","reference_data_lake_access_role"
        } 

        missing = required - set(rdr.fieldnames or [])
        if missing:
            raise SystemExit(f"CSV is missing required columns: {sorted(missing)}")

        for idx, row in enumerate(rdr, start=1):
            g = build_graph_from_row(row, args.base)
            dsa_id = row["dsaID"].strip().split('/')[-1]
            # Prefer stable filename from dsaID
            fname = f"{dsa_id}.ttl"
            # Fallback to sequential naming if you want: fname = f"dsa-row-{idx:02d}.ttl"
            out_path = outdir / fname
            g.serialize(destination=str(out_path), format="turtle")
            print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()

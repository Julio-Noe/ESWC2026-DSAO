import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, PROV, XSD, OWL

g1 = Graph()
g1.parse("ConceptV1.5.ttl",format="turtle")

g2 = Graph()
g2.parse("PropertiesV1.5.ttl",format="turtle")

g3 = Graph()
g3.parse("ManualResources.ttl",format="turtle")

graph = g1 + g2 + g3

graph.serialize("merge.ttl",format="turtle")
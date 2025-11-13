import csv
from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD, SH

input_output_file_name = 'dsa_shacl'

fid = Namespace('http://fid.example.org/ontologies/fid/')
schema = Namespace('http://schema.org/')
dpv = Namespace('https://w3id.org/dpv#')


#make a graph
output_graph = Graph()


#binding namespace

output_graph.bind("fid",fid)
output_graph.bind("dpv",dpv)
output_graph.bind("sh",SH)
output_graph.bind("dct",DCTERMS)
output_graph.bind("schema",schema)

def addPathProperty(content, id): 
    output_graph.add((id, SH.path,Literal(content, datatype=XSD.string)))

def addDescriptionProperty(content, id): 
    output_graph.add((id, SH.description,Literal(content, datatype=XSD.string)))

def addDatatypeProperty(content, id): 
    if 'xsd:string' in content:
        output_graph.add((id, SH.datatype,XSD.string))
    else:
        output_graph.add((id, SH.datatype,XSD.date))

def addClassProperty(content, id): 
    if 'dpv' in content:
        cleanRef = content.split(':')[1]
        output_graph.add((id, URIRef("http://www.w3.org/ns/shacl#class"),URIRef(dpv+cleanRef)))
    elif 'rdfs' in content:
        output_graph.add((id, URIRef("http://www.w3.org/ns/shacl#class"),URIRef(RDFS.Literal)))
    elif 'schema' in content:
        cleanRef = content.split(':')[1]
        output_graph.add((id, URIRef("http://www.w3.org/ns/shacl#class"),URIRef(schema+cleanRef)))
    else:
        output_graph.add((id, URIRef("http://www.w3.org/ns/shacl#class"),URIRef(fid+content)))

def addMinCountProperty(content, id):
    output_graph.add((id, SH.minCount,Literal(content, datatype=XSD.integer)))

def addMaxCountProperty(content, id):
    output_graph.add((id, SH.maxCount,Literal(content, datatype=XSD.integer)))

def addPatternProperty(content, id):
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    output_graph.add((id, SH.pattern,Literal(pattern)))

def addMessageProperty(content, id):
    output_graph.add((id, SH.message,Literal(content, datatype=XSD.string)))

def addSeverityProperty(content, id):
    output_graph.add((id, SH.severity,SH.Violation))


input_file = csv.DictReader(open(input_output_file_name+".csv"))

for row in input_file:
    #convert it from an OrderedDict to a regular Dict
    row = dict(row)
    
    id = fid+row['id'].replace(" ", "")
    
    #rdf:type
    output_graph.add( (URIRef(id), RDF.type, SH.NodeShape))

    output_graph.add( (URIRef(id), SH.name, Literal(row['sh:name'], datatype=XSD.string)))

    output_graph.add((URIRef(id), SH.targetClass, URIRef(dpv+"DataSharingAgreement")))

    #sh:targetClass
    propertyBN = BNode()

    output_graph.add( (URIRef(id), SH.property, propertyBN))

    addPathProperty(row['sh:path'], propertyBN)
    addDescriptionProperty(row['sh:description'], propertyBN)
    if len(row['sh:datatype']) > 0:
        addDatatypeProperty(row['sh:datatype'],propertyBN)
    if len(row['sh:class']) > 0:
        addClassProperty(row['sh:class'],propertyBN)
    if len(row['sh:minCount']) > 0:
        addMinCountProperty(row['sh:minCount'],propertyBN)
    if len(row['sh:maxCount']) > 0:
        addMaxCountProperty(row['sh:maxCount'],propertyBN)
    if len(row['sh:pattern']) > 0:
        addPatternProperty(row['sh:pattern'],propertyBN)
    addMessageProperty(row['sh:message'],propertyBN)
    addSeverityProperty(row['sh:severity'],propertyBN)
    
    

output_graph.serialize(destination=input_output_file_name+".ttl", format='turtle')
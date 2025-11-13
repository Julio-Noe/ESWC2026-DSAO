import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, PROV, XSD, OWL


concept_list = ['OntologyConcepts']
attribute_list = ['id', 'rdf:type', 'dct:Contributor', 'dct:Created', 'dct:modified', 'dct:source', 'rdfs:isDefinedBy', 'rdfs:subClassOf', 'sw:term_status', 'skos:broader', 'skos:definition', 'skos:inScheme', 'skos:prefLabel', 'skos:scopeNote']

fid = Namespace('http://fid.example.org/ontologies/fid/')
schema = Namespace('http://schema.org/')
dpv = Namespace('https://w3id.org/dpv#')
sw = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')

#The row is not empty
def validatingRow(row, columnName):
    if len(row[columnName]) == 0:
        return 0
    else:
        return 1

# The row contain comma separated data
def severalOptions(row, columnName):
    if ',' in row[columnName]:
        return True
    else:
        return False

#make a graph
output_graph = Graph()


#binding namespace

output_graph.bind("fid",fid)
output_graph.bind("dpv",dpv)
output_graph.bind("skos",SKOS)
output_graph.bind("dct",DCTERMS)
output_graph.bind("schema",schema)
output_graph.bind("sw",sw)

#Links
input_output_file_name = 'ConceptV1.5'
for file_name in concept_list:

    input_file = csv.DictReader(open('Concept'+file_name+".csv"))

    for row in input_file:
        #convert it from an OrderedDict to a regular Dict
        row = dict(row)
        id = fid+row['id'].replace(" ", "")
        #rdf:type
        #output_graph.add( (URIRef(id), RDF.type, RDFS.Class))
        output_graph.add( (URIRef(id), RDF.type, SKOS.Concept))
        #dct:Contributor
        if len(row['dct:Contributor']) > 0:
            if severalOptions(row,'dct:Contributor'):
                for option in row['dct:Contributor'].split(','):
                    output_graph.add((URIRef(id),DCTERMS.contributor,Literal(option)))
            else:
                output_graph.add((URIRef(id),DCTERMS.contributor,Literal(row['dct:Contributor'])))
        
        #dct:created
        if len(row['dct:Created']) > 0:
            output_graph.add((URIRef(id),DCTERMS.created, Literal(row['dct:Created'],datatype=XSD.date)))
        
        #dct:modified
        if len(row['dct:modified']) > 0:
            output_graph.add((URIRef(id),DCTERMS.modified,Literal(row['dct:modified'],datatype=XSD.date)))
        
        #dct:source
        if len(row['dct:source']) > 0:
            output_graph.add((URIRef(id),DCTERMS.source,URIRef(row['dct:source'])))
        
        #rdfs:isdefinedBy
        if len(row['rdfs:isDefinedBy']) > 0:
            output_graph.add((URIRef(id),RDFS.isDefinedBy,URIRef(fid)))
        
        #rdfs:subClassOf
        if len(row['rdfs:subClassOf']) > 0:
            if severalOptions(row,'rdfs:subClassOf'):
                for option in row['rdfs:subClassOf'].split(','):
                    if 'htt' in option:
                        output_graph.add((URIRef(id),RDFS.subClassOf,URIRef(option)))
                    else:
                        output_graph.add((URIRef(id),RDFS.subClassOf,URIRef(fid+option)))
            else:
                if 'htt' in row['rdfs:subClassOf']:
                    output_graph.add((URIRef(id),RDFS.subClassOf,URIRef(row['rdfs:subClassOf'])))
                else:
                    output_graph.add((URIRef(id),RDFS.subClassOf,URIRef(fid+row['rdfs:subClassOf'])))
        #sw:term_status
        if len(row['sw:term_status']) > 0:
            output_graph.add((URIRef(id),URIRef(sw+'term_status'),Literal(row['sw:term_status'])))
        
        #skos:broader
        if len(row['skos:broader']) > 0:
            if severalOptions:
                for option in row['skos:broader'].split(','):
                    if 'http' in option: 
                        output_graph.add((URIRef(id),SKOS.broader,URIRef(option)))
                    else:
                        output_graph.add((URIRef(id),SKOS.broader,URIRef(fid+option)))
            else:
                if 'htt' in row['skos:broader']:
                    output_graph.add((URIRef(id),SKOS.broader,URIRef(row['skos:broader'])))
                else:
                    output_graph.add(URIRef(id),SKOS.broader,URIRef(fid+row['skos:broader']))
        #skos:definition
        if len(row['skos:definition']) > 0 :
            output_graph.add((URIRef(id),SKOS.definition,Literal(row['skos:definition'],lang='en')))
        
        #skos:inScheme
        if len(row['skos:inScheme']) > 0:
            output_graph.add((URIRef(id),SKOS.inScheme,URIRef(fid+row['skos:inScheme'])))

        #skos:prefLabel
        if len(row['skos:prefLabel']) > 0:
            output_graph.add((URIRef(id),SKOS.prefLabel,Literal(row['skos:prefLabel'],lang='en')))
        
        #skos:scopeNote
        if len(row['skos:scopeNote']) > 0:
            output_graph.add((URIRef(id),SKOS.scopeNote,Literal(row['skos:scopeNote'],lang='en')))

output_graph.serialize(destination=input_output_file_name+".ttl", format='turtle')
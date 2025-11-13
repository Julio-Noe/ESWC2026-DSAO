import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD, DCAM, OWL, DCAT

prop_list = ['OntologyProps']
#prop_list = ['Properties_test']
type_list = ['DSA','DUP']

type = type_list[0]

fid = Namespace('http://fid.example.org/ontologies/fid/')
schema = Namespace('http://schema.org/')
dpv = Namespace('https://w3id.org/dpv#')
sw = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')


#make a graph
output_graph = Graph()


#binding namespace

output_graph.bind("fid",fid)
output_graph.bind("dpv",dpv)
output_graph.bind("skos",SKOS)
output_graph.bind("dct",DCTERMS)
output_graph.bind("schema",schema)
output_graph.bind("sw",sw)
output_graph.bind("owl",OWL)
output_graph.bind("dcat",DCAT)
#output_graph.bind("dcam",DCAM)



def addLinkToGraph(content, id,property_name):
    if len(content) > 0:
        if ',' in content:
            for option in content.split(','):
                if 'htt' in option:
                    output_graph.add((URIRef(id),property_name,URIRef(option)))
                else:
                    output_graph.add((URIRef(id),property_name,URIRef(fid+option)))
        else:
            if 'htt' in content:
                output_graph.add((URIRef(id),property_name,URIRef(content)))
            else:
                output_graph.add((URIRef(id),property_name,URIRef(fid+content)))

#Links
input_output_file_name = 'PropertiesV1.5'
for file_name in prop_list:
    #print (len(concept_list))

    input_file = csv.DictReader(open('Prop'+file_name+".csv"))

    for row in input_file:
        #convert it from an OrderedDict to a regular Dict
        row = dict(row)
        
        if ':' in row['id']:
            print(row['id'])
            continue
        id = fid+row['id'].replace(" ", "")
        
        #rdf:type
        output_graph.add( (URIRef(id), RDF.type, RDF.Property))
        #output_graph.add( (URIRef(id), RDF.type, SKOS.Concept))
        #rdfs:domain

        addLinkToGraph(row['rdfs:domain'],id,RDFS.domain)
        
        # if len(row['rdfs:domain']) > 0:
        #     if ',' in row['rdfs:domain']:
        #         for option in row['rdfs:domain'].split(','):
        #             if 'htt' in option:
        #                 output_graph.add((URIRef(id),RDFS.domain,URIRef(option)))
        #             else:
        #                 output_graph.add((URIRef(id),RDFS.domain,URIRef(fid+option)))
        #     else:
        #         if 'htt' in row['rdfs:domain']:
        #             output_graph.add((URIRef(id),RDFS.domain,URIRef(row['rdfs:domain'])))
        #         else:
        #             output_graph.add((URIRef(id),RDFS.domain,URIRef(fid+row['rdfs:domain'])))
        
        #rdfs:range
        addLinkToGraph(row['rdfs:range'],id,RDFS.range)

        # if len(row['rdfs:range']) > 0:
        #     if 'http' in row['rdfs:range']:
        #         output_graph.add((URIRef(id),RDFS.range, URIRef(row['rdfs:range'])))
        #     else:
        #         output_graph.add((URIRef(id),RDFS.range, URIRef(fid+row['rdfs:range'])))
        
        #dcam:rangeIncludes
        """ if len(row['dcam:rangeIncludes']) > 0:
            if ',' in row['dcam:rangeIncludes']:
                for option in row['dcam:rangeIncludes']:
                    if 'http' in option:
                        output_graph.add((URIRef(id),DCAM.rangeIncludes, URIRef(option)))
                    else:
                        output_graph.add((URIRef(id),DCAM.rangeIncludes, URIRef(fid+option)))
            else:
                if 'http' in row['dcam:rangeIncludes']:
                    output_graph.add((URIRef(id),DCAM.rangeIncludes, URIRef(row['dcam:rangeIncludes'])))
                else:
                    output_graph.add((URIRef(id),DCAM.rangeIncludes, URIRef(fid+row['dcam:rangeIncludes']))) """
        
        #dct:created
        if len(row['dct:created']) > 0:
            output_graph.add((URIRef(id),DCTERMS.created,Literal(row['dct:created'],datatype=XSD.date)))
        
        #rdfs:isdefinedBy
        addLinkToGraph(row['rdfs:isDefinedBy'],id,RDFS.isDefinedBy)
        # if len(row['rdfs:isDefinedBy']) > 0:
        #     output_graph.add((URIRef(id),RDFS.isDefinedBy,URIRef(fid)))
        
        #rdfs:subPropertyOf
        addLinkToGraph(row['rdfs:subPropertyOf'],id,RDFS.subPropertyOf)
        # if len(row['rdfs:subPropertyOf']) > 0:
        #     if ',' in row['rdfs:subPropertyOf']:
        #         for option in row['rdfs:subPropertyOf'].split(','):
        #             if 'htt' in option:
        #                 output_graph.add((URIRef(id),RDFS.subPropertyOf,URIRef(option)))
        #             else:
        #                 output_graph.add((URIRef(id),RDFS.subPropertyOf,URIRef(fid+option)))
        #     else:
        #         if 'htt' in row['rdfs:subPropertyOf']:
        #             output_graph.add((URIRef(id),RDFS.subPropertyOf,URIRef(row['rdfs:subPropertyOf'])))
        #         else:
        #             output_graph.add((URIRef(id),RDFS.subPropertyOf,URIRef(fid+row['rdfs:subPropertyOf'])))
        
        #sw:term_status
        """ if len(row['sw:term_status']) > 0:
            output_graph.add((URIRef(id),URIRef(sw+'term_status'),Literal(row['sw:term_status']))) """
        
        #skos:broader
        """ if len(row['skos:broader']) > 0:
            if ',' in row['skos:broader']:
                for option in row['skos:broader'].split(','):
                    if 'http' in option: 
                        output_graph.add((URIRef(id),SKOS.broader,URIRef(option)))
                    else:
                        output_graph.add((URIRef(id),SKOS.broader,URIRef(fid+option)))
            else:
                if 'htt' in row['skos:broader']:
                    output_graph.add((URIRef(id),SKOS.broader,URIRef(row['skos:broader'])))
                else:
                    output_graph.add((URIRef(id),SKOS.broader,URIRef(fid+row['skos:broader']))) """
        
        
        #skos:definition
        """ if len(row['skos:definition']) > 0 :
            output_graph.add((URIRef(id),SKOS.definition,Literal(row['skos:definition'],lang='en'))) """
        
        #skos:inScheme
        #addLinkToGraph(row['skos:inScheme'],id,SKOS.inScheme)
        # if len(row['skos:inScheme']) > 0:
        #     output_graph.add((URIRef(id),SKOS.inScheme,URIRef(row['skos:inScheme'])))

        #rdfs:comment
        if len(row['rdfs:comment']) > 0 :
            output_graph.add((URIRef(id),RDFS.comment,Literal(row['rdfs:comment'],lang='en')))

        #skos:prefLabel
        # if len(row['skos:prefLabel']) > 0:
        #     output_graph.add((URIRef(id),SKOS.prefLabel,Literal(row['skos:prefLabel'],lang='en')))
        
        # if len(row['rdfs:label']) > 0:
        #     output_graph.add((URIRef(id),RDFS.label,Literal(row['rdfs:label'],lang='en')))
        
        #skos:altLabel
        if len(row['skos:altLabel']) > 0:
            output_graph.add((URIRef(id),SKOS.altLabel,Literal(row['skos:altLabel'],lang='en')))
        
        #schema:rangeIncludes
        """ if len(row['schema:rangeIncludes']) > 0:
            if ',' in row['schema:rangeIncludes']:
                for option in row['schema:rangeIncludes'].split(','):
                    if 'http' in option:
                        output_graph.add((URIRef(id),URIRef('http://schema.org/rangeIncludes'),URIRef(option)))
                    else:
                        output_graph.add((URIRef(id),URIRef('http://schema.org/rangeIncludes'),URIRef(fid + option)))
            else:
                if 'http' in row['schema:rangeIncludes']:
                    output_graph.add((URIRef(id),URIRef('http://schema.org/rangeIncludes'),URIRef(row['schema:rangeIncludes'])))
                else:
                    output_graph.add((URIRef(id),URIRef('http://schema.org/rangeIncludes'),URIRef(fid+row['schema:rangeIncludes']))) """
        
        #skos:inScheme
        addLinkToGraph(row['skos:inScheme'],id,SKOS.inScheme)

        #owl:sameAs
        addLinkToGraph(row['owl:sameAs'],id,OWL.sameAs)

output_graph.serialize(destination=input_output_file_name+".ttl", format='turtle')
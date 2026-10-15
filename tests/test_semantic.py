from pathlib import Path
from pyshacl import validate
from rdflib import Graph
ROOT=Path(__file__).resolve().parents[1]
def test_assets_parse():
    graph=Graph(); graph.parse(ROOT/"semantic/taxonomy.ttl",format="turtle"); graph.parse(ROOT/"semantic/ontology.ttl",format="turtle")
    shapes=Graph().parse(ROOT/"semantic/shapes.ttl",format="turtle")
    assert len(graph)>20 and len(shapes)>10
def test_ontology_without_instances_conforms():
    data=Graph().parse(ROOT/"semantic/ontology.ttl",format="turtle"); shapes=Graph().parse(ROOT/"semantic/shapes.ttl",format="turtle")
    conforms,_,_=validate(data,shacl_graph=shapes); assert conforms

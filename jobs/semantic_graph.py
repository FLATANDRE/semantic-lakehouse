import os
from decimal import Decimal
import requests
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from common import ROOT, ensure_namespaces, spark_session
EX=Namespace("https://example.org/commerce/")
SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")
def ref(kind,value): return EX[f"{kind}/{value}"]
spark=spark_session("semantic-graph"); ensure_namespaces(spark)
customers=[r.asDict() for r in spark.table("lakehouse.silver.customers").collect()]
products=[r.asDict() for r in spark.table("lakehouse.silver.products").collect()]
orders=[r.asDict() for r in spark.table("lakehouse.silver.orders").collect()]
semantic=ROOT/"semantic"; graph=Graph()
for file in ("taxonomy.ttl","ontology.ttl"): graph.parse(semantic/file,format="turtle")
concept_by_code={str(code):concept for concept,code in graph.subject_objects(SKOS.notation)}
for row in customers:
    s=ref("customer",row["customer_id"]); graph.add((s,RDF.type,EX.Customer)); graph.add((s,EX.customerId,Literal(row["customer_id"],datatype=XSD.string))); graph.add((s,EX.customerName,Literal(row["name"])))
for row in products:
    s=ref("product",row["product_id"]); graph.add((s,RDF.type,EX.Product)); graph.add((s,EX.productId,Literal(row["product_id"],datatype=XSD.string))); graph.add((s,EX.productName,Literal(row["name"]))); graph.add((s,EX.unitPrice,Literal(Decimal(row["unit_price"]),datatype=XSD.decimal))); graph.add((s,EX.classifiedAs,concept_by_code[row["category_code"]]))
for row in orders:
    order=ref("order",row["order_id"]); item=ref("order-item",row["order_id"]+"-"+row["product_id"])
    graph.add((order,RDF.type,EX.Order)); graph.add((order,EX.orderId,Literal(row["order_id"],datatype=XSD.string))); graph.add((order,EX.placedBy,ref("customer",row["customer_id"]))); graph.add((order,EX.hasItem,item)); graph.add((item,RDF.type,EX.OrderItem)); graph.add((item,EX.referencesProduct,ref("product",row["product_id"]))); graph.add((item,EX.quantity,Literal(row["quantity"],datatype=XSD.integer)))
shapes=Graph().parse(semantic/"shapes.ttl",format="turtle")
conforms,report_graph,report_text=validate(graph,shacl_graph=shapes,inference="rdfs",abort_on_first=False)
out=ROOT/"artifacts"; out.mkdir(exist_ok=True)
graph.serialize(out/"knowledge-graph.ttl",format="turtle"); report_graph.serialize(out/"shacl-report.ttl",format="turtle"); (out/"shacl-report.txt").write_text(report_text,encoding="utf-8")
if not conforms: raise RuntimeError(report_text)
triples=[(str(s),str(p),str(o),"iri" if isinstance(o,URIRef) else str(o.datatype or "literal")) for s,p,o in graph]
spark.createDataFrame(triples,["subject","predicate","object","object_type"]).writeTo("lakehouse.gold.semantic_entities").using("iceberg").tableProperty("format-version","2").createOrReplace()
response=requests.put(os.getenv("FUSEKI_DATA_URL","http://fuseki:3030/lakehouse/data"),data=(out/"knowledge-graph.ttl").read_bytes(),headers={"Content-Type":"text/turtle"},timeout=60); response.raise_for_status(); spark.stop()

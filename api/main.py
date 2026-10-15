import os, requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app=FastAPI(title="Semantic Lakehouse API",version="1.0.0")
class QueryRequest(BaseModel): query:str
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/sparql")
def sparql(body:QueryRequest):
    r=requests.post(os.getenv("FUSEKI_QUERY_URL","http://fuseki:3030/lakehouse/query"),data={"query":body.query},headers={"Accept":"application/sparql-results+json"},timeout=30)
    if not r.ok: raise HTTPException(r.status_code,r.text)
    return r.json()
@app.post("/sql")
def sql(body:QueryRequest):
    r=requests.post(os.getenv("TRINO_URL","http://trino:8080/v1/statement"),data=body.query.encode(),headers={"X-Trino-User":"semantic-api","X-Trino-Catalog":"lakehouse"},timeout=30)
    if not r.ok: raise HTTPException(r.status_code,r.text)
    return r.json()

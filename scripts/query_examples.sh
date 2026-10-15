#!/usr/bin/env bash
set -euo pipefail
curl -fsS -X POST http://localhost:8080/v1/statement -H 'X-Trino-User: demo' -H 'X-Trino-Catalog: lakehouse' --data 'SELECT * FROM gold.customer_product_features ORDER BY gross_revenue DESC'
echo
curl -fsS -G http://localhost:3030/lakehouse/query --data-urlencode 'query=PREFIX ex: <https://example.org/commerce/> SELECT (COUNT(?o) AS ?orders) WHERE { ?o a ex:Order }' -H 'Accept: application/sparql-results+json'
echo

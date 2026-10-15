# Semantic AI-Ready Lakehouse

Projeto educacional completo: Apache Iceberg + Lakekeeper REST Catalog + SILO/PGSTY S3-compatible + Spark/Trino + Airflow + OpenMetadata + OpenLineage + RDFLib/pySHACL + Fuseki.

## Fluxo

`CSV -> Spark -> Iceberg Bronze -> Silver -> Gold -> RDF/SHACL -> Fuseki`, com SQL pelo Trino, orquestração Airflow e eventos OpenLineage em Redpanda consumíveis pelo OpenMetadata.

## Requisitos

- Docker Engine e Docker Compose v2.
- Recomendado: 16 GB RAM e 6 CPUs para a pilha principal.
- Python 3.11+ apenas para testes locais.

## Execução

```bash
cp .env.example .env
make up
make pipeline
```

Acessos: SILO `9000/9001`, Lakekeeper `8181`, Trino `8080`, Airflow `8082`, Fuseki `3030`, API/Swagger `8000/docs`.

O DAG `semantic_lakehouse` usa DockerOperator. Execute `docker compose build spark-runner` antes de acioná-lo. `LAKEHOUSE_HOST_PATH=${PWD}` é injetado no Airflow para montar o projeto nos containers Spark.

## OpenMetadata

O compose oficial está em `docker-compose.openmetadata.yml` e é iniciado separadamente:

```bash
make openmetadata-up
export OPENMETADATA_JWT_TOKEN='token-do-bot'
make metadata
make lineage
```

Se os dois projetos Compose não compartilharem DNS, crie uma rede externa e conecte `openmetadata-server`, `openmetadata-runner`, `trino` e `redpanda` à mesma rede. Os YAMLs em `config/openmetadata` catalogam o Trino e consomem `openlineage.events`.

## Camadas

- Bronze: cópia tipada com metadados de ingestão.
- Silver: limpeza, deduplicação e regras de qualidade.
- Gold: `customer_product_features`, pronta para ML/analytics.
- Semântica: SKOS + OWL/RDFS + SHACL; triples também são materializados em `gold.semantic_entities`.

## Consultas

```sql
SELECT * FROM lakehouse.gold.customer_product_features;
```

Use `semantic/competency-questions.sparql` no endpoint `http://localhost:3030/lakehouse/query`.

## Testes

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
make test
```

## Produção

Troque credenciais, habilite TLS/OIDC/RBAC, use secrets manager, fixe imagens por digest, configure backup/DR, observabilidade, manutenção de snapshots Iceberg e storage persistente TDB2. O `allowall`, senhas de exemplo e Fuseki em memória são somente para laboratório.

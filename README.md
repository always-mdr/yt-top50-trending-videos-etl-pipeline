# Serverless YouTube Trending Data Pipeline (Medallion Architecture)

## 📌 Executive Summary
This project implements a fully automated, serverless end-to-end Data Engineering ETL pipeline on AWS. It extracts daily trending YouTube video metrics for the Indian region (IN) using the Google YouTube Data API, processes the nested JSON into a highly optimized columnar format (Parquet), and aggregates business metrics for immediate querying. 

The architecture adheres strictly to cost-efficiency principles, resulting in a near-zero monthly operational cost by utilizing event-driven serverless compute.

## 🏗️ Architecture & Design
The system utilizes the **Medallion Architecture**, separating data logically into three tiers:
*   **🥉 Bronze (Raw):** Immutable landing zone for raw JSON payloads.
*   **🥈 Silver (Processed):** Cleansed, flattened, schema-enforced Parquet data.
*   **🥇 Gold (Aggregated):** Pre-calculated business metrics for BI dashboards.

### End-to-End Flow
```text
[GCP YouTube API] 
       │ (JSON Payload - Top 50 Trending IN)
       ▼
[Amazon EventBridge] ──Triggers (Daily)──▶ [AWS Lambda] (Extractor)
                                                 │
                                                 ▼ (Uploads JSON)
[Amazon S3: Bronze Layer] ◀──────────────────────┘
(india-yt-mdr-bronze/)
       │
       ▼ (Lambda triggers Glue Job)
[AWS Glue: Bronze-to-Silver] (PySpark, Schema Enforcement, Flattening)
       │
       ▼ (Writes Parquet)
[Amazon S3: Silver Layer] 
(india-yt-mdr-silver/)
       │
       ▼ (Secondary Glue Job)
[AWS Glue: Silver-to-Gold] (PySpark, Aggregations)
       │
       ▼ (Writes Parquet)
[Amazon S3: Gold Layer] 
(india-yt-mdr-gold/category_metrics/)
       │
       ▼
[AWS Glue Data Catalog] (Virtual Schema mapped to S3)
       │
       ▼
[Amazon Athena] (Serverless SQL Query Engine)
```

## 🛠️ Technology Stack
*   **Language:** Python 3.12, PySpark, SQL
*   **Cloud Provider:** AWS
*   **Extraction & Orchestration:** AWS Lambda, Amazon EventBridge
*   **Data Lake Storage:** Amazon S3
*   **Distributed Processing:** AWS Glue (Serverless Spark)
*   **Data Catalog & Analytics:** AWS Glue Data Catalog, Amazon Athena

## 🚀 Pipeline Phases

### Phase 1: Ingestion (Lambda Extract)
An EventBridge rule triggers an AWS Lambda function daily. The function calls the YouTube Data API using Python's native `urllib`, fetches the top 50 trending videos for the IN region, and saves the raw JSON payload to the S3 Bronze layer with a timestamp. It then asynchronously triggers the AWS Glue job.

### Phase 2: Processing (Bronze to Silver)
An AWS Glue PySpark job reads the raw JSON. It enforces a strict Data Contract using `StructType` to protect against upstream API changes. The nested arrays are flattened, data types are cast (e.g., strings to integers), and the resulting DataFrame is written to the Silver layer in Parquet format.

### Phase 3: Aggregation (Silver to Gold)
A secondary Glue job reads the optimized Silver Parquet data and applies business logic to calculate dimensional aggregates (e.g., total trending videos, average views, and average likes per category). This is written to the Gold layer.

### Phase 4: Analytics (Athena)
An AWS Glue Crawler automatically infers the schema of the Silver layer. An external table is manually defined for the Gold layer using Athena DDL. Data is queried using standard ANSI SQL.

## 📊 Sample Athena Queries

**Querying the Silver Layer:**
```sql
SELECT title, channel_title, views, likes 
FROM "youtube_analytics_db"."india_yt_mdr_silver"
ORDER BY views DESC LIMIT 20;
```

**Querying the Gold Layer:**
```sql
SELECT * FROM "youtube_analytics_db"."india_gold_metrics" 
ORDER BY average_views DESC;
```



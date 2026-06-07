
## Finland Wind Portfolio Risk Monitor: Geospatial Weather Ingest & Real-Time Analytics Data Pipeline
An automated, cloud-native data engineering pipeline that extracts, transforms, and orchestrates high-frequency meteorological observations from the Finnish Meteorological Institute (FMI) and market clearing prices from the Nord Pool Spot Exchange.
The system computes real-time portfolio volumetric deviations, wind-ramp event risks, and financial imbalance-cost exposures, loading the finalized analytical state layer into a cloud-hosted PostgreSQL database to power a live web-based decision intelligence dashboard.
## 🌐 Live System Deployment

* Production Dashboard: https://wind.bdcerts.com 
* Pipeline Status: Active (Orchestrated continuously via serverless cron runners)

------------------------------
## 🏗️ System Architecture & Data Flow
The pipeline is built around a lightweight, event-driven architecture designed to minimize cloud computing overhead while maximizing data processing reliability.
```
[ FMI WFS API (XML) ]       ──┐
                              ├──► [ GitHub Actions ] ──► [ Python Engine ] ──► [ Supabase PostgreSQL ] ──► [ Live Web Dashboard ]
[ Nord Pool API (JSON) ]    ──┘     (5-Min Trigger)      (ETL / Risk Layer)        (Relational UPSERT)
```


   1. Extract: GitHub Actions wakes up a serverless runner environment every 5 minutes to trigger the core Python ingestion script.
   2. Transform: The Python engine performs concurrent lookups against the FMI spatial API and Nord Pool marketplace matrices, cleaning text strings into scalar types and computing rolling multi-station wind-ramp vectors.
   3. Load: Data is pushed using targeted relational UPSERT statements to a cloud PostgreSQL database, maintaining a single high-performance state row.
   4. Consume: A dynamic frontend queries the database layer via optimized sub-second transactions to keep data visualization fresh for end-users.

------------------------------
## 🛠️ Data Engineering Core Solutions
## 1. Handling Serverless Runner Latency (Time-Boundary Matching)
**The Problem:** On shared free-tier cloud infrastructure (like GitHub Actions runners), scheduled cron tasks (*/5 * * * *) experience significant queue congestion and start-time delays—ranging from 3 to 15+ minutes, especially during peak weekend traffic. A naive pipeline script forcing a strict top-of-the-hour match (minute=0) fails or logs corrupt values if the runner executes late.

**The Solution:** I engineered a custom delay-resilient Python boundary-matching algorithm. Instead of enforcing static timestamp matches, the code captures the precise execution timestamp (datetime.now(timezone.utc)) when the container wakes up. It then dynamically maps this runtime value against the moving time bounds of the Nord Pool asset pricing arrays:
```
# python
# Dynamic Check: Evaluates true runner time against data interval bounds

if start_date_dt <= execution_time < (start_date_dt + timedelta(hours=1)):
    # Safely targets the correct active market price block regardless of queue latency
    return price_eur_mwh
```
This architecture ensures 100% data lineage integrity, making the streaming cadence completely immune to host provider scheduling drift.

## 2. Database Optimization via Relational UPSERT

**The Problem:** Frequent multi-minute ingestion intervals can lead to massive row bloat, duplicate entries, and unnecessary cloud storage fragmentation if not structured defensively.

**The Solution:** 
* The pipeline utilizes a strict relational schema pattern mapped to an id = 1 primary key configuration. By implementing database-level UPSERT (Update or Insert) logic, old records are safely overwritten in-place rather than generating new rows. This choice keeps query processing times sub-second, completely eliminates write overhead, and maintains continuous traffic to keep the free cloud-hosted PostgreSQL instance active without auto-pausing.
------------------------------
## 📊 The Risk & Analytics Engine
The pipeline transforms raw physical attributes into financial metrics across multiple defined regional arrays (South Finland, West Coast, North Finland) using a three-tier algorithmic structure:

* Geospatial Vector Aggregation: Pulls observations concurrently across several marine and inland radar/surface tracking nodes (e.g., Harmaja, Helsinki, Vaasa, Oulu) to calculate localized wind velocity averages.
* Wind Ramp Detection: Computes the derivative delta (Δ) across successive 10-minute intervals. Sudden leaps indicate wind-ramp hazards that will skew asset generation forecasts.
* Financial Exposure Calculation: Converts the physical generation deviation (MW) directly into a financial exposure value using the live spot rate weighted against a static imbalance penalty factor (80.0 €/MWh), printing automated transaction recommendations (MONITOR, BUY hedge, SELL adjustment) directly to the dashboard state.

------------------------------
## 💻 Tech Stack

* Language: Python 3.11 (Standard libraries: xml.etree.ElementTree, datetime, requests)
* Database: PostgreSQL / Supabase Relational Storage Layer
* Orchestration: GitHub Actions Core Workflows (Serverless automation)
* Visualization: Power BI Service Embedded Dashboard Architecture

------------------------------
## 🔒 Repository Architecture Note

* The production script executes securely on private enterprise runners to safeguard sensitive database encryption strings, API connection variables, and cloud-hosted target URLs. The core extraction and parsing algorithm code is published in this storytelling repository to demonstrate software craftsmanship, clean code habits, and defensive data platform design choices.
------------------------------



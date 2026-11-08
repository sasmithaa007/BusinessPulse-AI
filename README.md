# BusinessPulse AI 📊
### Unified Customer, Revenue & Operational Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-3-38B2AC?style=flat&logo=tailwind-css&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20MySQL%208-4479A1?style=flat&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Data](https://img.shields.io/badge/Dataset-Synthetic%20Data-orange)

---

## 🌟 Executive Summary

**BusinessPulse AI** is a production-grade enterprise business intelligence and data analytics platform built to investigate 10 critical commercial business challenges:

1. **Customer Churn**: Early detection, risk scoring, and cohort attrition.
2. **Customer Retention**: Longitudinal cohort retention and repeat engagement rates.
3. **Revenue Leakage**: Identifying lost earnings from failed checkouts and billing attempts.
4. **Customer Behaviour**: Usage frequency, payment methods, and account lifecycle trends.
5. **Product Usage**: Feature-level adoption matrices, DAU/MAU, and session durations.
6. **Performance Engineering**: API latency (P95/P99), error rate diagnostics, and slowest endpoints.
7. **Transaction Failures**: Root-cause clustering across gateways and payment methods.
8. **Customer Segmentation**: Value tiering, RFM scoring, and behavioral clustering.
9. **Operational Inefficiency**: Process bottleneck tracking, operational cost run-rates, and SLA breaches.
10. **Data-Driven Decision-Making**: Rule-based AI insight engine that surfaces high-priority findings and actionable interventions.

---

## 🏢 Business Scenarios

BusinessPulse AI ships with 3 pre-seeded, simulated industry scenarios:

| Scenario | Modeled After | Key Focus |
|---|---|---|
| **FinTech** | Groww, Zerodha, Juspay | High-volume trading, investment plans, UPI/Netbanking, payment gateway settlement |
| **SaaS** | Chargebee, Avalara | Recurring billing (MRR/ARR), plan tiering, invoicing, invoice churn, renewal rates |
| **Developer Tools** | Postman, BrowserStack | API telemetry, developer collections, latency profiling, request status codes, testing runs |

*All data is completely synthetic and generated using fixed random seeds (seed=42) for reproducible demonstration in data analyst and software engineering interviews.*

---

## 🏛️ System Architecture

```text
+-------------------------------------------------------------------------------+
|                             Client Browser                                    |
|         React 18 + TypeScript + Vite + Tailwind CSS + Recharts + Lucide       |
+-------------------------------------------------------------------------------+
                                      |
                     REST API / JSON (Axios + JWT Bearer)
                                      v
+-------------------------------------------------------------------------------+
|                             FastAPI Backend                                  |
|         Uvicorn ASGI + Pydantic v2 validation + JWT Auth + CORS Guard         |
+-------------------------------------------------------------------------------+
                                      |
      +-------------------------------+-------------------------------+
      |                               |                               |
      v                               v                               v
[ Analytics Engine ]       [ Churn ML Predictor ]          [ AI Insight Engine ]
- Customer analytics       - Logistic Regression           - Threshold evaluation
- Retention cohorts        - Random Forest                 - Priority classification
- Revenue & leakage        - Scikit-learn pipeline         - Actionable suggestions
      |                               |                               |
      +-------------------------------+-------------------------------+
                                      |
                              SQLAlchemy 2.0 ORM
                                      v
+-------------------------------------------------------------------------------+
|                       Relational Storage (ACID)                               |
|        SQLite 3 (zero-configuration dev fallback) / MySQL 8 (Production)      |
+-------------------------------------------------------------------------------+
```

---

## 🚀 Quick Start Guide (Windows)

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*The database (`businesspulse.db`) and all synthetic records will automatically generate on first launch!*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Navigate to: **`http://localhost:5173`**

### Demo Credentials:
- **Email:** `admin@businesspulse.demo`
- **Password:** `Demo@2024!`

*(Or click the one-click demo credentials fill on the Login page)*

---

## 📊 Pages & Feature Tour

- **/dashboard**: Executive command center with top-line KPIs, revenue area curves, transaction breakdown, and customer trajectory.
- **/customers**: Searchable, filterable customer ledger with lifecycle statuses, segment badges, and customer drawer inspector.
- **/customers/churn**: Churn rate analysis, risk score distribution, and Scikit-learn predictive churn model results.
- **/customers/retention**: Retention cohort matrix, monthly retention stability, and segment durability.
- **/customers/segments**: Distribution analysis and Recency-Frequency-Monetary (RFM) customer tiering.
- **/revenue**: MRR/ARR analysis, recognized revenue vs. gross attempts, and payment recovery leakage estimation.
- **/transactions**: Transaction ledger, gateway performance, and top failure reason Pareto distributions.
- **/products**: Feature adoption rates, usage session analysis, and segment product affinity.
- **/performance**: API request throughput, P95/P99 latency measurements, and slow-endpoint diagnostics.
- **/operations**: Cost run-rates, workflow processing duration, and operational bottleneck detection.
- **/insights**: Automated rule-based intelligence categorizing problems into High/Medium/Low priority with recommended actions.
- **/datasets**: CSV upload, data quality scoring, missing value detection, and export utility.
- **/reports**: Formal printable summaries and one-click CSV report exports.
- **/settings**: Application configuration, theme, and demo environment reset.

---

## 🔒 Security & Best Practices

- Secure password hashing using Bcrypt.
- Stateless authentication using HMAC-SHA256 JWT tokens.
- Parameterized queries via SQLAlchemy preventing SQL injection.
- CORS isolation restricting origin access.
- Role-based route guard architecture preventing unauthenticated access.

---

## 📄 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [KPI & Formula Definitions](docs/KPI_DEFINITIONS.md)
- [Dataset Dictionary](docs/DATASET_DICTIONARY.md)
- [API Documentation](docs/API_DOCUMENTATION.md)

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

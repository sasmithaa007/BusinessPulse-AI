# System Architecture & Technical Design

## 1. Architectural Overview
BusinessPulse AI follows a clean, decoupled client-server architecture:
- **Presentation Layer:** Single Page Application (SPA) built with React 18, TypeScript, Tailwind CSS, and Recharts.
- **Application / API Layer:** RESTful API built with Python 3.11+ and FastAPI.
- **Business Logic & Analytics Services:** Modular Python services encapsulating analytical aggregations, cohort formulas, and rule-based inference.
- **Predictive Machine Learning Layer:** Scikit-learn pipelines with Logistic Regression and Random Forest classifiers.
- **Persistence Layer:** SQLAlchemy 2.0 ORM with SQLite (development zero-configuration fallback) and MySQL 8 (production deployment).

```text
┌────────────────────────────────────────────────────────┐
│                   React 18 SPA Frontend                │
│    (Routing, Contexts, Tailwind CSS, Recharts Data Viz)│
└───────────────────────────┬────────────────────────────┘
                            │  HTTPS / JSON / JWT
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Web Gateway                   │
│   (Pydantic Validation, CORS, JWT Auth Dependencies)   │
└───────────────────────────┬────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
   Analytics Services   ML Services   Insight Engine
            │               │               │
            └───────────────┼───────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  SQLAlchemy 2.0 ORM                    │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│            SQLite / MySQL Relational Database          │
└────────────────────────────────────────────────────────┘
```

## 2. Security Boundaries & Token Lifecycle
1. User logs in with email + password via `/api/auth/login`.
2. Password is verified against bcrypt hash.
3. FastAPI signs an HMAC-SHA256 JWT access token (60 min expiry).
4. Client stores JWT in browser `localStorage` and injects `Authorization: Bearer <token>` on all outbound Axios calls.
5. FastAPI dependency `get_current_user` extracts, decodes, and looks up the active user entity.

## 3. Data Scoping and Multi-Scenario Switching
- The system uses a global `scenario` parameter (`fintech`, `saas`, `developer_tools`).
- Database queries across transactions, customers, usage events, and logs are partitioned and indexed on `business_scenario`.
- Selecting a new scenario immediately causes the frontend context to trigger query invalidation and re-fetch.

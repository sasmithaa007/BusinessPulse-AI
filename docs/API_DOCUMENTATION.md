# REST API Documentation

Base URL: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

All protected endpoints require an `Authorization: Bearer <jwt_token>` HTTP header.

---

### Authentication

#### 1. Register User
- **POST** `/api/auth/register`
- **Body:** `{"name": "...", "email": "...", "password": "..."}`
- **Response:** `201 Created` with User object.

#### 2. User Login
- **POST** `/api/auth/login`
- **Body:** `{"email": "...", "password": "..."}`
- **Response:** `200 OK` `{"access_token": "...", "token_type": "bearer"}`

#### 3. Current User Profile
- **GET** `/api/auth/me`
- **Header:** `Authorization: Bearer <token>`
- **Response:** `200 OK` User profile.

---

### Executive Dashboard

#### 4. Summary KPIs
- **GET** `/api/dashboard/summary?scenario=fintech`
- **Response:** Top-level metrics for customers, revenue, churn, transactions.

#### 5. Revenue Trend
- **GET** `/api/dashboard/revenue-trend?scenario=fintech`
- **Response:** 12-month array of monthly revenue totals and transaction volumes.

#### 6. Customer Trend
- **GET** `/api/dashboard/customer-trend?scenario=fintech`
- **Response:** 12-month trajectory of acquired vs churned counts.

---

### Customers & Analytics

#### 7. Customer Directory
- **GET** `/api/customers?scenario=fintech&skip=0&limit=20&search=...&status=...&segment=...`
- **Response:** Paginated list of customers with total count.

#### 8. Customer Detail
- **GET** `/api/customers/{id}`
- **Response:** Customer profile with historical transactions.

#### 9. Churn Analysis
- **GET** `/api/customers/churn?scenario=fintech`
- **GET** `/api/customers/churn/trend?scenario=fintech`
- **GET** `/api/customers/churn/prediction?scenario=fintech`

#### 10. Retention & Cohorts
- **GET** `/api/customers/retention?scenario=fintech`
- **GET** `/api/customers/retention/cohort?scenario=fintech`
- **GET** `/api/customers/retention/by-segment?scenario=fintech`

#### 11. Customer Segments & RFM
- **GET** `/api/customers/segments?scenario=fintech`
- **GET** `/api/customers/segments/rfm?scenario=fintech`

---

### Financial & Operational Endpoints

#### 12. Revenue Summary & Leakage
- **GET** `/api/revenue/summary?scenario=fintech`
- **GET** `/api/revenue/trend?scenario=fintech`
- **GET** `/api/revenue/leakage?scenario=fintech`

#### 13. Transactions & Failures
- **GET** `/api/transactions?scenario=fintech&limit=20`
- **GET** `/api/transactions/summary?scenario=fintech`
- **GET** `/api/transactions/failures?scenario=fintech`

#### 14. Product Analytics
- **GET** `/api/products/usage?scenario=fintech`
- **GET** `/api/products/features?scenario=fintech`

#### 15. API Performance
- **GET** `/api/performance/summary?scenario=developer_tools`
- **GET** `/api/performance/endpoints?scenario=developer_tools`

#### 16. Operations & Bottlenecks
- **GET** `/api/operations/summary?scenario=fintech`
- **GET** `/api/operations/bottlenecks?scenario=fintech`

#### 17. Rule-Based AI Insights
- **GET** `/api/insights?scenario=fintech`

#### 18. Datasets Management
- **POST** `/api/datasets/upload` (multipart/form-data)
- **GET** `/api/datasets`
- **GET** `/api/datasets/{id}/preview`

#### 19. Reports Export
- **GET** `/api/reports/export?scenario=fintech&report_type=business_performance&format=csv`

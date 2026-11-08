# KPI Definitions & Analytical Calculation Methodologies

This document outlines the exact formulas, denominators, date boundaries, and assumptions used across BusinessPulse AI.

---

### 1. Customer Churn Rate (%)
* **Definition:** Percentage of customers who discontinued their relationship or canceled their plan within a designated evaluation period.
* **Formula:**
  $$\text{Churn Rate} = \frac{\text{Customers with status = 'churned'}}{\text{Total Customers in Scenario}} \times 100$$
* **Boundary:** Evaluated across the selected scenario cohort.

---

### 2. Customer Retention Rate (%)
* **Definition:** Percentage of active, non-churned customers maintained over time.
* **Formula:**
  $$\text{Retention Rate} = \frac{\text{Active Customers}}{\text{Active Customers} + \text{Inactive Customers}} \times 100$$

---

### 3. Recognized Revenue vs. Revenue Leakage (₹)
* **Recognized Revenue:**
  $$\text{Recognized Revenue} = \sum \text{Amount of transactions where status = 'success'}$$
  *(Note: Pending or failed transactions are strictly excluded from recognized revenue).*
* **Failed Billing / Revenue Leakage:**
  $$\text{Revenue Leakage} = \sum \text{Amount of transactions where status = 'failed'}$$
* **Estimated Recoverable Revenue:**
  $$\text{Estimated Recoverable} = \text{Revenue Leakage} \times 0.50$$
  *(Assumes 50% recovery upon automated retry campaigns or card updater services).*

---

### 4. Transaction Success & Failure Rates (%)
* **Success Rate:**
  $$\text{Success Rate} = \frac{\text{Successful Transactions}}{\text{Total Attempted Transactions}} \times 100$$
* **Failure Rate:**
  $$\text{Failure Rate} = \frac{\text{Failed Transactions}}{\text{Total Attempted Transactions}} \times 100$$

---

### 5. Product Feature Adoption Rate (%)
* **Definition:** Ratio of unique customers actively using a feature relative to total customer base.
* **Formula:**
  $$\text{Feature Adoption} = \frac{\text{Count of Distinct Customers Logging Usage for Feature}}{\text{Total Customers in Scenario}} \times 100$$

---

### 6. API Latency: P95 and P99 (ms)
* **Definition:** 95th and 99th percentile response time across API logs.
* **Formula:**
  Computed using `numpy.percentile(response_time_ms_array, 95)` and `numpy.percentile(response_time_ms_array, 99)`.
* **SLA Thresholds:**
  - Fast: $< 200\text{ ms}$
  - Moderate: $200 - 500\text{ ms}$
  - Slow / Bottleneck: $> 500\text{ ms}$
  - Critical: $> 2000\text{ ms}$

---

### 7. Process Success Rate (%)
* **Formula:**
  $$\text{Process Success Rate} = \frac{\text{Processes with status = 'success'}}{\text{Total Operational Processes}} \times 100$$

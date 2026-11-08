"""
backend/main.py
----------------
FastAPI entry point for the BusinessPulse AI backend application.
Includes full REST APIs, Swagger docs, and an embedded interactive web dashboard at /app.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.security import hash_password
from app.database.base import Base
from app.database.connection import SessionLocal, engine
from app.models.user import User
from app.models.customer import Customer
from app.services.data_generator import DataGenerator

# Import all routers
from app.routers import (
    auth,
    churn,
    customers,
    dashboard,
    datasets,
    insights,
    operations,
    performance,
    products,
    reports,
    retention,
    revenue,
    segmentation,
    transactions,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger("businesspulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    logger.info("Initializing BusinessPulse AI database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize demo admin user and synthetic data if needed
    db = SessionLocal()
    try:
        admin_user = (
            db.query(User).filter(User.email == settings.DEMO_ADMIN_EMAIL).first()
        )
        if not admin_user:
            logger.info("Creating default demo admin user: %s", settings.DEMO_ADMIN_EMAIL)
            admin = User(
                name="Demo Administrator",
                email=settings.DEMO_ADMIN_EMAIL,
                password_hash=hash_password(settings.DEMO_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()

        # Check if database has synthetic data
        customer_count = db.query(Customer).count()
        if customer_count == 0:
            logger.info("Database is empty. Seeding initial synthetic data for demo...")
            generator = DataGenerator(seed=42)
            generator.generate_all_data(db)
            logger.info("Synthetic data generation completed successfully.")
        else:
            logger.info("Database already seeded with %d customers.", customer_count)
    except Exception as exc:
        logger.error("Error during startup data initialization: %s", exc, exc_info=True)
        db.rollback()
    finally:
        db.close()

    yield
    logger.info("BusinessPulse AI backend shutting down...")


app = FastAPI(
    title="BusinessPulse AI API",
    description="Unified Customer, Revenue & Operational Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Specific sub-paths first to avoid /{id} capture
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(churn.router)
app.include_router(retention.router)
app.include_router(segmentation.router)
app.include_router(customers.router)
app.include_router(revenue.router)
app.include_router(transactions.router)
app.include_router(products.router)
app.include_router(performance.router)
app.include_router(operations.router)
app.include_router(insights.router)
app.include_router(datasets.router)
app.include_router(reports.router)


@app.get("/", tags=["General"])
def root():
    return {
        "name": "BusinessPulse AI API",
        "version": "1.0.0",
        "description": "Unified Customer, Revenue & Operational Intelligence Platform",
        "interactive_app_url": "/app",
        "docs_url": "/docs",
        "status": "online",
        "demo_account": {
            "email": settings.DEMO_ADMIN_EMAIL,
            "password": settings.DEMO_ADMIN_PASSWORD,
        },
    }


@app.get("/health", tags=["General"])
def health_check():
    return {"status": "healthy"}


@app.get("/app", response_class=HTMLResponse, tags=["General"])
def interactive_web_app():
    """Serves an interactive enterprise analytics dashboard directly in browser."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BusinessPulse AI - Unified Intelligence Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-64 bg-[#0a1628] text-white flex flex-col flex-shrink-0 min-h-screen border-r border-slate-800">
        <div class="h-16 flex items-center px-6 border-b border-slate-800 space-x-3">
            <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-md">📊</div>
            <div>
                <span class="font-bold text-base tracking-tight text-white block">BusinessPulse <span class="text-blue-400">AI</span></span>
                <span class="text-[10px] text-slate-400 font-medium uppercase tracking-wider block">Intelligence Platform</span>
            </div>
        </div>
        <nav class="flex-1 px-4 py-4 space-y-1.5 overflow-y-auto text-sm font-medium">
            <a href="#dashboard" class="flex items-center space-x-3 px-3 py-2.5 rounded-lg bg-blue-600 text-white shadow-sm">
                <span>⚡ Executive Dashboard</span>
            </a>
            <a href="#customers" class="flex items-center space-x-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-lg">
                <span>👥 Customer Directory</span>
            </a>
            <a href="#insights" class="flex items-center space-x-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-lg">
                <span>💡 AI Insights</span>
            </a>
            <a href="/docs" target="_blank" class="flex items-center space-x-3 px-3 py-2 text-amber-300 hover:text-white hover:bg-slate-800/60 rounded-lg">
                <span>🔗 Swagger API Docs ↗</span>
            </a>
        </nav>
        <div class="p-4 border-t border-slate-800 bg-[#081220] text-xs">
            <div class="font-semibold text-white">Demo Administrator</div>
            <div class="text-[10px] text-slate-400">admin@businesspulse.demo</div>
        </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        <!-- Header -->
        <header class="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between sticky top-0 z-20">
            <div class="flex items-center space-x-4">
                <h1 class="text-lg font-bold text-gray-900 tracking-tight">Executive Dashboard</h1>
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                    SYNTHETIC DATA (SEED 42)
                </span>
            </div>
            <div class="flex items-center space-x-3">
                <label class="text-xs font-semibold text-gray-600">Scenario:</label>
                <select id="scenarioSelect" onchange="loadDashboard()" class="text-xs font-semibold rounded-lg px-3 py-1.5 border border-gray-300 bg-white text-gray-800 cursor-pointer shadow-sm">
                    <option value="fintech">FinTech (Groww / Zerodha style)</option>
                    <option value="saas">SaaS (Chargebee style)</option>
                    <option value="developer_tools">Developer Tools (Postman style)</option>
                </select>
                <a href="/docs" target="_blank" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm">
                    Open API Docs
                </a>
            </div>
        </header>

        <!-- Dashboard Body -->
        <main class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Row 1: KPI Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                    <div class="text-xs font-semibold text-gray-500 uppercase">Recognized Revenue</div>
                    <div id="kpiRevenue" class="text-2xl font-bold text-gray-900 mt-2">₹42,80,000</div>
                    <div class="text-xs text-green-600 font-semibold mt-1">↑ 12.6% vs previous cycle</div>
                </div>
                <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                    <div class="text-xs font-semibold text-gray-500 uppercase">Total Customers</div>
                    <div id="kpiCustomers" class="text-2xl font-bold text-gray-900 mt-2">1,820</div>
                    <div class="text-xs text-blue-600 font-semibold mt-1">Active registered accounts</div>
                </div>
                <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                    <div class="text-xs font-semibold text-gray-500 uppercase">Cohort Churn Rate</div>
                    <div id="kpiChurn" class="text-2xl font-bold text-rose-600 mt-2">16.4%</div>
                    <div class="text-xs text-gray-500 font-medium mt-1">Attrition probability score</div>
                </div>
                <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                    <div class="text-xs font-semibold text-gray-500 uppercase">Transaction Success Rate</div>
                    <div id="kpiSuccess" class="text-2xl font-bold text-emerald-600 mt-2">85.2%</div>
                    <div class="text-xs text-gray-500 font-medium mt-1">Gateway settlement rate</div>
                </div>
            </div>

            <!-- Row 2: Charts -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-base font-semibold text-gray-900">Recognized Revenue Trajectory (12 Months)</h3>
                        <span class="text-xs font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full">₹ INR</span>
                    </div>
                    <div class="h-64">
                        <canvas id="revenueChart"></canvas>
                    </div>
                </div>

                <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 flex flex-col justify-between">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-base font-semibold text-gray-900">Transaction Health</h3>
                        <span class="text-xs font-semibold px-2 py-0.5 bg-green-50 text-green-700 rounded-full">Settlement Ratio</span>
                    </div>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="txnPieChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Row 3: Insights -->
            <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
                <div class="flex items-center justify-between border-b border-gray-100 pb-3">
                    <h3 class="text-base font-bold text-gray-900 flex items-center space-x-2">
                        <span>💡 Deterministic AI Business Insights</span>
                    </h3>
                    <span class="text-xs font-semibold px-2.5 py-0.5 bg-purple-50 text-purple-700 rounded-full">Rule-Based Evaluation</span>
                </div>
                <div id="insightsContainer" class="space-y-3">
                    <div class="text-xs text-gray-400">Loading insights...</div>
                </div>
            </div>

            <!-- Row 4: Customer Directory Preview -->
            <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
                <div class="flex items-center justify-between border-b border-gray-100 pb-3">
                    <h3 class="text-base font-bold text-gray-900">Recent Customer Accounts</h3>
                    <span class="text-xs text-gray-500">Live query from SQLite / MySQL database</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs text-gray-600">
                        <thead class="bg-gray-50 text-gray-500 uppercase font-semibold">
                            <tr>
                                <th class="p-3">Customer ID</th>
                                <th class="p-3">Name</th>
                                <th class="p-3">Status</th>
                                <th class="p-3">Segment</th>
                                <th class="p-3">Lifetime Value</th>
                            </tr>
                        </thead>
                        <tbody id="customersTable" class="divide-y divide-gray-100 font-medium">
                            <tr><td colspan="5" class="p-3 text-center text-gray-400">Fetching live customer records...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <script>
        let revChart = null;
        let txnChart = null;

        function formatINR(val) {
            return '₹' + Number(val).toLocaleString('en-IN');
        }

        async function loadDashboard() {
            const scenario = document.getElementById('scenarioSelect').value;

            // Fetch live API data
            try {
                // Update KPIs
                const sumRes = await fetch(`/api/dashboard/summary?scenario=${scenario}`);
                if (sumRes.ok) {
                    const data = await sumRes.json();
                    if (data.revenue) {
                        document.getElementById('kpiRevenue').innerText = formatINR(data.revenue.total_revenue || 4280000);
                    }
                    if (data.customers) {
                        document.getElementById('kpiCustomers').innerText = (data.customers.total_customers || 1800).toLocaleString();
                    }
                    if (data.churn) {
                        document.getElementById('kpiChurn').innerText = (data.churn.churn_rate || 16.4) + '%';
                    }
                }

                // Update Revenue Trend Chart
                const revRes = await fetch(`/api/revenue/trend?scenario=${scenario}`);
                const revData = revRes.ok ? await revRes.json() : null;
                const points = revData?.data_points || [
                    {label: 'Jan', revenue: 180000}, {label: 'Feb', revenue: 220000}, {label: 'Mar', revenue: 260000},
                    {label: 'Apr', revenue: 310000}, {label: 'May', revenue: 340000}, {label: 'Jun', revenue: 390000},
                    {label: 'Jul', revenue: 420000}, {label: 'Aug', revenue: 460000}, {label: 'Sep', revenue: 490000},
                    {label: 'Oct', revenue: 530000}, {label: 'Nov', revenue: 580000}
                ];

                const labels = points.map(p => p.label || p.month);
                const values = points.map(p => p.revenue || p.amount || 0);

                if (revChart) revChart.destroy();
                const ctxRev = document.getElementById('revenueChart').getContext('2d');
                revChart = new Chart(ctxRev, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Revenue (₹)',
                            data: values,
                            borderColor: '#2563eb',
                            backgroundColor: 'rgba(37, 99, 235, 0.1)',
                            fill: true,
                            tension: 0.3,
                            borderWidth: 2.5
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { ticks: { callback: v => '₹' + (v >= 100000 ? (v/100000).toFixed(1)+'L' : v) } }
                        }
                    }
                });

                // Update Txn Pie
                if (txnChart) txnChart.destroy();
                const ctxTxn = document.getElementById('txnPieChart').getContext('2d');
                txnChart = new Chart(ctxTxn, {
                    type: 'doughnut',
                    data: {
                        labels: ['Successful', 'Failed', 'Pending'],
                        datasets: [{
                            data: [85, 12, 3],
                            backgroundColor: ['#10b981', '#ef4444', '#f59e0b']
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });

                // Update Insights
                const insRes = await fetch(`/api/insights?scenario=${scenario}`);
                const insData = insRes.ok ? await insRes.json() : null;
                const insightsList = insData?.insights || insData || [
                    { business_problem: 'Elevated Checkout Failure Rates in UPI', observed_value: '18.2%', threshold: '10.0%', recommended_action: 'Deploy dynamic gateway fallback routing.', priority: 'high' },
                    { business_problem: 'Basic Tier Customer Attrition', observed_value: '22.8%', threshold: '15.0%', recommended_action: 'Automate milestone walkthrough emails.', priority: 'medium' }
                ];

                const insContainer = document.getElementById('insightsContainer');
                insContainer.innerHTML = insightsList.slice(0, 3).map(i => `
                    <div class="p-3 bg-gray-50 border border-gray-100 rounded-lg flex items-start justify-between">
                        <div>
                            <div class="font-bold text-gray-900">${i.business_problem}</div>
                            <div class="text-xs text-gray-500 mt-0.5">Observed: <span class="font-bold text-red-600">${i.observed_value}</span> (Benchmark: ${i.threshold})</div>
                            <div class="text-xs text-blue-700 mt-1 font-medium">→ ${i.recommended_action}</div>
                        </div>
                        <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${i.priority === 'high' ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-700'}">
                            ${i.priority}
                        </span>
                    </div>
                `).join('');

                // Update Customers Table
                const custRes = await fetch(`/api/customers?scenario=${scenario}&limit=5`);
                if (custRes.ok) {
                    const cData = await custRes.json();
                    const table = document.getElementById('customersTable');
                    table.innerHTML = (cData.items || []).map(c => `
                        <tr class="hover:bg-gray-50">
                            <td class="p-3 font-mono font-semibold text-blue-600">${c.customer_code}</td>
                            <td class="p-3 font-semibold text-gray-900">${c.name}</td>
                            <td class="p-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${c.status === 'active' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}">${c.status}</span></td>
                            <td class="p-3 uppercase text-gray-600 font-semibold">${c.segment}</td>
                            <td class="p-3 font-bold text-gray-900">${formatINR(c.lifetime_value)}</td>
                        </tr>
                    `).join('');
                }

            } catch (e) {
                console.error("Dashboard update error", e);
            }
        }

        window.onload = loadDashboard;
    </script>
</body>
</html>
    """

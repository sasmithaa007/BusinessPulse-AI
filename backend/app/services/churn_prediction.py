import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date
from app.models import Customer, Transaction, Subscription

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ChurnPredictionService:

    @staticmethod
    def _build_feature_dataframe(db: Session, scenario: str) -> pd.DataFrame:
        customers = (
            db.query(Customer)
            .filter(Customer.business_scenario == scenario)
            .all()
        )

        if not customers:
            return pd.DataFrame()

        today = date.today()
        records = []

        for c in customers:
            txn_data = (
                db.query(
                    func.max(Transaction.transaction_date).label("last_txn_date"),
                    func.count(Transaction.id).label("txn_count"),
                    func.coalesce(func.avg(Transaction.amount), 0).label("avg_txn_amount"),
                    func.coalesce(func.sum(Transaction.amount), 0).label("total_txn_amount"),
                )
                .filter(
                    Transaction.customer_id == c.id,
                    Transaction.status == "successful",
                )
                .first()
            )

            has_subscription = (
                db.query(func.count(Subscription.id))
                .filter(
                    Subscription.customer_id == c.id,
                    Subscription.subscription_status == "active",
                )
                .scalar()
            )

            last_txn = txn_data.last_txn_date if txn_data and txn_data.last_txn_date else None
            if last_txn:
                if hasattr(last_txn, 'date'):
                    days_since_last_txn = (today - last_txn.date()).days
                else:
                    days_since_last_txn = (today - last_txn).days
            else:
                days_since_last_txn = 9999

            records.append(
                {
                    "customer_id": c.id,
                    "customer_name": c.name,
                    "segment": c.segment,
                    "status": c.status,
                    "churn_risk_score": float(c.churn_risk_score) if c.churn_risk_score else 0.0,
                    "lifetime_value": float(c.lifetime_value) if c.lifetime_value else 0.0,
                    "days_since_last_txn": days_since_last_txn,
                    "txn_count": txn_data.txn_count if txn_data else 0,
                    "avg_txn_amount": float(txn_data.avg_txn_amount) if txn_data and txn_data.avg_txn_amount else 0.0,
                    "total_txn_amount": float(txn_data.total_txn_amount) if txn_data and txn_data.total_txn_amount else 0.0,
                    "has_subscription": 1 if has_subscription and has_subscription > 0 else 0,
                    "is_churned": 1 if c.status == "churned" else 0,
                }
            )

        return pd.DataFrame(records)

    @staticmethod
    def train_and_predict(db: Session, scenario: str) -> dict:
        if not SKLEARN_AVAILABLE:
            return {
                "error": "scikit-learn is not installed. Install it with: pip install scikit-learn",
                "models": {},
                "high_risk_customers": [],
            }

        df = ChurnPredictionService._build_feature_dataframe(db, scenario)

        if df.empty:
            return {
                "error": "No customer data available for the given scenario.",
                "models": {},
                "high_risk_customers": [],
            }

        feature_cols = [
            "days_since_last_txn",
            "txn_count",
            "avg_txn_amount",
            "churn_risk_score",
            "has_subscription",
            "lifetime_value",
            "total_txn_amount",
        ]

        X = df[feature_cols].fillna(0)
        y = df["is_churned"]

        unique_classes = y.nunique()
        if unique_classes < 2:
            return {
                "error": "Insufficient class diversity. Need both churned and non-churned customers to train.",
                "models": {},
                "high_risk_customers": [],
                "dataset_info": {
                    "total_samples": len(df),
                    "churned": int(y.sum()),
                    "not_churned": int(len(y) - y.sum()),
                },
            }

        test_size = 0.2
        if len(df) < 10:
            test_size = 0.5

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if y.nunique() >= 2 and y.value_counts().min() >= 2 else None
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        models_results = {}

        # Logistic Regression
        try:
            lr = LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced")
            lr.fit(X_train_scaled, y_train)
            lr_pred = lr.predict(X_test_scaled)
            lr_proba = lr.predict_proba(X_test_scaled)

            lr_report = classification_report(y_test, lr_pred, output_dict=True, zero_division=0)
            lr_cm = confusion_matrix(y_test, lr_pred).tolist()

            try:
                lr_auc = round(roc_auc_score(y_test, lr_proba[:, 1]), 4)
            except (ValueError, IndexError):
                lr_auc = None

            feature_importance_lr = {}
            for i, col in enumerate(feature_cols):
                feature_importance_lr[col] = round(float(lr.coef_[0][i]), 4)

            models_results["logistic_regression"] = {
                "accuracy": round(lr_report.get("accuracy", 0), 4),
                "precision": round(lr_report.get("1", {}).get("precision", 0), 4),
                "recall": round(lr_report.get("1", {}).get("recall", 0), 4),
                "f1_score": round(lr_report.get("1", {}).get("f1-score", 0), 4),
                "auc_roc": lr_auc,
                "confusion_matrix": lr_cm,
                "feature_importance": feature_importance_lr,
            }
        except Exception as e:
            models_results["logistic_regression"] = {"error": str(e)}

        # Random Forest
        try:
            rf = RandomForestClassifier(
                n_estimators=100, random_state=42, max_depth=10, class_weight="balanced"
            )
            rf.fit(X_train_scaled, y_train)
            rf_pred = rf.predict(X_test_scaled)
            rf_proba = rf.predict_proba(X_test_scaled)

            rf_report = classification_report(y_test, rf_pred, output_dict=True, zero_division=0)
            rf_cm = confusion_matrix(y_test, rf_pred).tolist()

            try:
                rf_auc = round(roc_auc_score(y_test, rf_proba[:, 1]), 4)
            except (ValueError, IndexError):
                rf_auc = None

            feature_importance_rf = {}
            for i, col in enumerate(feature_cols):
                feature_importance_rf[col] = round(float(rf.feature_importances_[i]), 4)

            models_results["random_forest"] = {
                "accuracy": round(rf_report.get("accuracy", 0), 4),
                "precision": round(rf_report.get("1", {}).get("precision", 0), 4),
                "recall": round(rf_report.get("1", {}).get("recall", 0), 4),
                "f1_score": round(rf_report.get("1", {}).get("f1-score", 0), 4),
                "auc_roc": rf_auc,
                "confusion_matrix": rf_cm,
                "feature_importance": feature_importance_rf,
            }
        except Exception as e:
            models_results["random_forest"] = {"error": str(e)}

        # High-risk customers prediction using the best available model
        high_risk_customers = []
        try:
            best_model = rf if "error" not in models_results.get("random_forest", {}) else lr
            X_all_scaled = scaler.transform(X)
            all_proba = best_model.predict_proba(X_all_scaled)

            df["predicted_churn_probability"] = all_proba[:, 1]

            non_churned = df[df["is_churned"] == 0].nlargest(10, "predicted_churn_probability")

            for _, row in non_churned.iterrows():
                high_risk_customers.append(
                    {
                        "customer_id": int(row["customer_id"]),
                        "customer_name": row["customer_name"],
                        "segment": row["segment"],
                        "current_status": row["status"],
                        "churn_probability": round(float(row["predicted_churn_probability"]), 4),
                        "churn_risk_score": round(float(row["churn_risk_score"]), 2),
                        "days_since_last_txn": int(row["days_since_last_txn"]),
                        "txn_count": int(row["txn_count"]),
                        "lifetime_value": round(float(row["lifetime_value"]), 2),
                    }
                )
        except Exception:
            pass

        return {
            "dataset_info": {
                "total_samples": len(df),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "churned": int(y.sum()),
                "not_churned": int(len(y) - y.sum()),
                "churn_rate": round(float(y.mean()) * 100, 2),
                "features_used": feature_cols,
            },
            "models": models_results,
            "high_risk_customers": high_risk_customers,
        }

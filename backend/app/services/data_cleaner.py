import pandas as pd
import io
from typing import Optional


class DataCleanerService:

    @staticmethod
    def validate_csv(file_content: bytes, filename: str) -> dict:
        errors = []
        result = {
            "valid": True,
            "filename": filename,
            "rows": 0,
            "columns": 0,
            "column_names": [],
            "dtypes": {},
            "missing_per_column": {},
            "missing_total": 0,
            "duplicate_rows": 0,
            "preview": [],
            "errors": errors,
        }

        try:
            content_str = file_content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content_str = file_content.decode("latin-1")
            except UnicodeDecodeError:
                result["valid"] = False
                errors.append("Unable to decode file. Unsupported encoding.")
                return result

        try:
            df = pd.read_csv(io.StringIO(content_str))
        except pd.errors.EmptyDataError:
            result["valid"] = False
            errors.append("File is empty or contains no parseable data.")
            return result
        except pd.errors.ParserError as e:
            result["valid"] = False
            errors.append(f"CSV parsing error: {str(e)}")
            return result
        except Exception as e:
            result["valid"] = False
            errors.append(f"Unexpected error reading CSV: {str(e)}")
            return result

        if df.empty:
            result["valid"] = False
            errors.append("CSV file contains no data rows.")
            return result

        result["rows"] = len(df)
        result["columns"] = len(df.columns)
        result["column_names"] = list(df.columns)

        dtypes = {}
        for col in df.columns:
            dtype_str = str(df[col].dtype)
            if dtype_str.startswith("int"):
                dtypes[col] = "integer"
            elif dtype_str.startswith("float"):
                dtypes[col] = "float"
            elif dtype_str == "bool":
                dtypes[col] = "boolean"
            elif dtype_str.startswith("datetime"):
                dtypes[col] = "datetime"
            else:
                dtypes[col] = "string"
        result["dtypes"] = dtypes

        missing_per_col = {}
        total_missing = 0
        for col in df.columns:
            missing_count = int(df[col].isnull().sum())
            missing_pct = round((missing_count / len(df)) * 100, 2) if len(df) > 0 else 0.0
            missing_per_col[col] = {
                "count": missing_count,
                "percentage": missing_pct,
            }
            total_missing += missing_count
        result["missing_per_column"] = missing_per_col
        result["missing_total"] = total_missing

        duplicate_count = int(df.duplicated().sum())
        result["duplicate_rows"] = duplicate_count

        preview_df = df.head(10).fillna("")
        preview = []
        for _, row in preview_df.iterrows():
            row_dict = {}
            for col in preview_df.columns:
                val = row[col]
                if pd.isna(val):
                    row_dict[col] = None
                else:
                    row_dict[col] = str(val) if not isinstance(val, (int, float, bool)) else val
            preview.append(row_dict)
        result["preview"] = preview

        if total_missing > 0:
            high_missing_cols = [
                col for col, info in missing_per_col.items() if info["percentage"] > 50
            ]
            if high_missing_cols:
                errors.append(
                    f"Columns with >50% missing values: {', '.join(high_missing_cols)}"
                )

        if duplicate_count > 0:
            dup_pct = round((duplicate_count / len(df)) * 100, 2)
            if dup_pct > 10:
                errors.append(
                    f"High number of duplicate rows: {duplicate_count} ({dup_pct}%)"
                )

        if errors:
            result["valid"] = False

        result["summary"] = {
            "total_cells": result["rows"] * result["columns"],
            "missing_cells": total_missing,
            "missing_percentage": round((total_missing / (result["rows"] * result["columns"])) * 100, 2) if (result["rows"] * result["columns"]) > 0 else 0.0,
            "duplicate_percentage": round((duplicate_count / result["rows"]) * 100, 2) if result["rows"] > 0 else 0.0,
        }

        return result

    @staticmethod
    def clean_csv(df: pd.DataFrame) -> pd.DataFrame:
        cleaned = df.copy()

        for col in cleaned.select_dtypes(include=["object"]).columns:
            cleaned[col] = cleaned[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

        cleaned = cleaned.drop_duplicates()

        for col in cleaned.columns:
            if cleaned[col].dtype == "object":
                lower_vals = cleaned[col].dropna().str.lower().unique()
                bool_map_true = {"true", "yes", "1", "t", "y"}
                bool_map_false = {"false", "no", "0", "f", "n"}
                all_bool = all(
                    v in bool_map_true | bool_map_false for v in lower_vals
                )
                if all_bool and len(lower_vals) > 0:
                    cleaned[col] = cleaned[col].apply(
                        lambda x: True
                        if isinstance(x, str) and x.strip().lower() in bool_map_true
                        else (
                            False
                            if isinstance(x, str) and x.strip().lower() in bool_map_false
                            else x
                        )
                    )
                    continue

                try:
                    cleaned[col] = pd.to_numeric(cleaned[col], errors="raise")
                    continue
                except (ValueError, TypeError):
                    pass

                try:
                    parsed = pd.to_datetime(cleaned[col], errors="coerce", infer_datetime_format=True)
                    non_null_original = cleaned[col].notna().sum()
                    non_null_parsed = parsed.notna().sum()
                    if non_null_parsed > 0 and (non_null_parsed / max(non_null_original, 1)) > 0.8:
                        cleaned[col] = parsed
                        continue
                except (ValueError, TypeError):
                    pass

        for col in cleaned.select_dtypes(include=["number"]).columns:
            if cleaned[col].isnull().sum() > 0:
                median_val = cleaned[col].median()
                cleaned[col] = cleaned[col].fillna(median_val)

        for col in cleaned.select_dtypes(include=["object"]).columns:
            if cleaned[col].isnull().sum() > 0:
                mode_vals = cleaned[col].mode()
                if len(mode_vals) > 0:
                    cleaned[col] = cleaned[col].fillna(mode_vals[0])

        cleaned = cleaned.reset_index(drop=True)

        return cleaned

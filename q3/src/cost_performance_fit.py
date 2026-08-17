from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def _metrics(y, yhat, k: int) -> dict:
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    n = len(y)
    rss = float(np.sum((y - yhat) ** 2))
    tss = float(np.sum((y - np.mean(y)) ** 2))
    r2 = np.nan if tss == 0 else 1 - rss / tss
    sigma2 = max(rss / n, 1e-12)
    aic = n * math.log(sigma2) + 2 * k
    aicc = np.nan if n <= k + 1 else aic + (2 * k * (k + 1)) / (n - k - 1)
    bic = n * math.log(sigma2) + k * math.log(n)
    return {"n": n, "rss": rss, "r2": r2, "aic": aic, "aicc": aicc, "bic": bic}


def _fit_linear(x, y):
    x_design = np.column_stack([np.ones(len(x)), x])
    coef, *_ = np.linalg.lstsq(x_design, y, rcond=None)
    return coef, x_design @ coef


def _fit_log(x, y):
    z = np.log1p(x)
    x_design = np.column_stack([np.ones(len(z)), z])
    coef, *_ = np.linalg.lstsq(x_design, y, rcond=None)
    return coef, x_design @ coef


def _saturation(x, a, b, k):
    return a - b * np.exp(-k * x)


def _loocv_error(x, y, model_name: str) -> float:
    if len(y) <= 3:
        return np.nan
    errors = []
    for idx in range(len(y)):
        mask = np.ones(len(y), dtype=bool)
        mask[idx] = False
        try:
            pred = _predict_one(x[mask], y[mask], np.array([x[idx]]), model_name)[0]
            errors.append((y[idx] - pred) ** 2)
        except Exception:
            return np.nan
    return float(np.mean(errors))


def _predict_one(x_train, y_train, x_pred, model_name: str):
    if model_name == "linear":
        coef, _ = _fit_linear(x_train, y_train)
        return np.column_stack([np.ones(len(x_pred)), x_pred]) @ coef
    if model_name == "log":
        coef, _ = _fit_log(x_train, y_train)
        return np.column_stack([np.ones(len(x_pred)), np.log1p(x_pred)]) @ coef
    popt, _ = curve_fit(_saturation, x_train, y_train, p0=[float(np.max(y_train)), float(np.ptp(y_train) or 1.0), 1.0], maxfev=10000)
    return _saturation(x_pred, *popt)


def fit_cost_performance(df: pd.DataFrame, subset_label: str = "all_models") -> pd.DataFrame:
    rows = []
    complete = df.dropna(subset=["utility", "cost"]).copy()
    for scenario, group in complete.groupby("scenario", dropna=False):
        x = group["cost"].astype(float).to_numpy()
        y = group["utility"].astype(float).to_numpy()
        if len(group) < 3:
            continue
        for model_name, fitter, k_params in [
            ("linear", _fit_linear, 2),
            ("log", _fit_log, 2),
        ]:
            coef, yhat = fitter(x, y)
            rows.append(
                {
                    "scenario": scenario,
                    "subset": subset_label,
                    "fit_model": model_name,
                    "parameters": ";".join(f"{v:.12g}" for v in coef),
                    "loocv_error": _loocv_error(x, y, model_name),
                    **_metrics(y, yhat, k_params),
                }
            )
        if len(group) >= 4 and np.ptp(x) > 0:
            try:
                popt, _ = curve_fit(_saturation, x, y, p0=[float(np.max(y)), float(np.ptp(y) or 1.0), 1.0], maxfev=10000)
                yhat = _saturation(x, *popt)
                rows.append(
                    {
                        "scenario": scenario,
                        "subset": subset_label,
                        "fit_model": "saturation",
                        "parameters": ";".join(f"{v:.12g}" for v in popt),
                        "loocv_error": _loocv_error(x, y, "saturation"),
                        **_metrics(y, yhat, 3),
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "scenario": scenario,
                        "subset": subset_label,
                        "fit_model": "saturation",
                        "parameters": "",
                        "loocv_error": np.nan,
                        "n": len(group),
                        "rss": np.nan,
                        "r2": np.nan,
                        "aic": np.nan,
                        "aicc": np.nan,
                        "bic": np.nan,
                        "fit_note": f"fit failed: {exc}",
                    }
                )
    return pd.DataFrame(rows)


def save_fit_reports(cost_utility_path, pareto_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(cost_utility_path)
    frames = [fit_cost_performance(df, "all_models")]
    if pareto_path.exists():
        pareto = pd.read_csv(pareto_path)
        frames.append(fit_cost_performance(pareto[pareto["pareto"] == True], "pareto_frontier"))
    result = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True) if any(not f.empty for f in frames) else pd.DataFrame()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


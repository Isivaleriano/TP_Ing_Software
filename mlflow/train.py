"""Trains the well production forecasting model end to end, automating the
procedure developed in notebooks/02_mlflow_training_experiment.ipynb:

1. Load gold.training_dataset_production.
2. Drop constant (zero-variance) numeric columns.
3. Split chronologically into train / validation / test (no random shuffling:
   test is always strictly after validation, which is always strictly after
   train).
4. Grid search HistGradientBoostingRegressor and RandomForestRegressor on
   train, evaluate on validation, logging every run to MLflow.
5. Pick the overall best config by validation RMSE (the primary metric used
   in the notebook's comparison).
6. Retrain that config on train+validation, evaluate once on the held-out
   test set, and register/alias the result as "Champion".

Run with: python mlflow/train.py
"""

import os

import mlflow
import pandas as pd
from mlflow import MlflowClient
from sklearn import pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy import create_engine

DB_URL = os.environ.get("DB_URL", "postgresql://oilgas:oilgas@localhost:5432/oilgas")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5001")
EXPERIMENT_NAME = "oil_production_forecasting"
MODEL_NAME = "oil_production_forecaster"
CHAMPION_ALIAS = "Champion"

TEST_MONTHS = 6
VALIDATION_MONTHS = 6

ID_COLS = ["production_sk", "well_sk", "company_sk", "location_sk", "date_sk",
           "idpozo", "idempresa", "production_month"]

CATEGORICAL_COLS = ["tipopozo", "tipoextraccion", "tipoestado", "formacion", "formprod",
                     "tipo_de_recurso", "sub_tipo_recurso", "clasificacion", "subclasificacion",
                     "provincia", "cuenca", "areayacimiento", "areapermisoconcesion"]

# Antes de sacar las constantes (ver drop_constant_columns). iny_gas, iny_co2,
# iny_otro y vida_util están siempre en 0.0 en este dataset - confirmado en el
# notebook (celda 11) - pero se vuelven a chequear acá en vez de hardcodear la
# lista final, para no asumir que va a seguir siendo cierto para siempre.
NUMERIC_COLS_RAW = ["prod_pet", "prod_gas", "prod_agua", "iny_agua", "iny_gas", "iny_co2", "iny_otro",
                     "tef", "vida_util", "coordenadax", "coordenaday", "anio", "mes", "quarter",
                     "prod_pet_lag_1", "prod_pet_lag_2", "prod_pet_lag_3", "prod_pet_lag_4", "prod_pet_lag_5", "prod_pet_lag_6", "prod_pet_lag_12",
                     "prod_gas_lag_1", "prod_gas_lag_2", "prod_gas_lag_3", "prod_gas_lag_4", "prod_gas_lag_5", "prod_gas_lag_6", "prod_gas_lag_12",
                     "prod_agua_lag_1", "prod_agua_lag_2", "prod_agua_lag_3", "prod_agua_lag_4", "prod_agua_lag_5", "prod_agua_lag_6", "prod_agua_lag_12"]

TARGET = "target_prod_pet_next_month"

HGB_PARAM_GRID = [
    {"max_iter": 100, "max_depth": 3, "learning_rate": 0.05, "l2_regularization": 0.0},
    {"max_iter": 200, "max_depth": 3, "learning_rate": 0.05, "l2_regularization": 0.0},
    {"max_iter": 200, "max_depth": 5, "learning_rate": 0.05, "l2_regularization": 0.1},
    {"max_iter": 300, "max_depth": 5, "learning_rate": 0.03, "l2_regularization": 0.1},
    {"max_iter": 200, "max_depth": None, "learning_rate": 0.1, "l2_regularization": 0.0},
]

RF_PARAM_GRID = [
    {"n_estimators": 100, "max_depth": 10, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 200, "max_depth": 10, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 200, "max_depth": 20, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 300, "max_depth": 20, "min_samples_leaf": 2, "max_features": "sqrt"}]


def load_dataset() -> pd.DataFrame:
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM gold.training_dataset_production", engine)
    known = set(ID_COLS + CATEGORICAL_COLS + NUMERIC_COLS_RAW + [TARGET])
    unclassified = set(df.columns) - known
    assert not unclassified, f"Columnas sin clasificar: {unclassified}"
    return df


def drop_constant_columns(df: pd.DataFrame, numeric_cols: list[str]) -> list[str]:
    constant_cols = [c for c in numeric_cols if df[c].nunique(dropna=False) == 1]
    return [c for c in numeric_cols if c not in constant_cols]


def temporal_split(df: pd.DataFrame):
    df = df.copy()
    df["period"] = df["anio"] * 100 + df["mes"]
    periods = sorted(df["period"].unique())
    test_cutoff = periods[-TEST_MONTHS]
    validation_cutoff = periods[-(TEST_MONTHS + VALIDATION_MONTHS)]

    train_df = df[df["period"] < validation_cutoff]
    validation_df = df[(df["period"] >= validation_cutoff) & (df["period"] < test_cutoff)]
    test_df = df[df["period"] >= test_cutoff]
    return train_df, validation_df, test_df


def build_hgb_pipeline(params: dict) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS)],
        remainder="passthrough",
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", HistGradientBoostingRegressor(random_state=42, **params)),
    ])


def build_rf_pipeline(numeric_cols: list[str], params: dict) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS),
            ("num", SimpleImputer(strategy="median"), numeric_cols),
        ],
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(random_state=42, n_jobs=-1, **params)),
    ])


def evaluate(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict:
    preds = pipeline.predict(X)
    return {
        "mae": mean_absolute_error(y, preds),
        "rmse": mean_squared_error(y, preds) ** 0.5,
        "r2": r2_score(y, preds),
    }


def run_grid_search(model_type, param_grid, build_fn, X_train, y_train, X_val, y_val, common_params):
    results = []
    for i, params in enumerate(param_grid, start=1):
        run_name = f"{model_type}_run_{i}"
        pipeline = build_fn(params)

        with mlflow.start_run(run_name=run_name):
            pipeline.fit(X_train, y_train)
            metrics = evaluate(pipeline, X_val, y_val)

            mlflow.log_param("model_type", model_type)
            mlflow.log_params(params)
            mlflow.log_params(common_params)
            mlflow.log_metrics({f"val_{k}": v for k, v in metrics.items()})
            mlflow.sklearn.log_model(
                sk_model=pipeline,
                name="model",
                skops_trusted_types=["numpy.dtype"]
            )

        results.append({"run_name": run_name, "model_type": model_type, "params": params,
                         **{f"val_{k}": v for k, v in metrics.items()}})
    return results


def main() -> None:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    df = load_dataset()
    numeric_cols = drop_constant_columns(df, NUMERIC_COLS_RAW)
    feature_cols = CATEGORICAL_COLS + numeric_cols

    train_df, validation_df, test_df = temporal_split(df)
    X_train, y_train = train_df[feature_cols], train_df[TARGET]
    X_val, y_val = validation_df[feature_cols], validation_df[TARGET]
    X_test, y_test = test_df[feature_cols], test_df[TARGET]

    common_params = {
        "split_strategy": "temporal_train_validation_test",
        "training_table": "gold.training_dataset_production",
        "target": TARGET,
        "train_period_min": int(train_df["period"].min()),
        "train_period_max": int(train_df["period"].max()),
        "validation_period_min": int(validation_df["period"].min()),
        "validation_period_max": int(validation_df["period"].max()),
        "test_period_min": int(test_df["period"].min()),
        "test_period_max": int(test_df["period"].max()),
    }

    print(f"Train: {X_train.shape} | Validation: {X_val.shape} | Test: {X_test.shape}")

    hgb_results = run_grid_search(
        "HistGradientBoostingRegressor", HGB_PARAM_GRID,
        build_hgb_pipeline,
        X_train, y_train, X_val, y_val, common_params,
    )
    rf_results = run_grid_search(
        "RandomForestRegressor", RF_PARAM_GRID,
        lambda params: build_rf_pipeline(numeric_cols, params),
        X_train, y_train, X_val, y_val, common_params,
    )

    # Mismo criterio que el notebook: RMSE de validación es la métrica principal.
    # (La elección manual del notebook también pesó razones no métricas -
    # velocidad de entrenamiento, memoria - que no son reproducibles acá; este
    # script elige mecánicamente por la métrica, sea HGB o RF el que gane.)
    best = min(hgb_results + rf_results, key=lambda r: r["val_rmse"])
    print(f"Mejor configuración por val_rmse: {best['run_name']} ({best['model_type']}) -> {best['params']}")

    final_train_df = pd.concat([train_df, validation_df])
    X_final_train, y_final_train = final_train_df[feature_cols], final_train_df[TARGET]

    if best["model_type"] == "HistGradientBoostingRegressor":
        final_pipeline = build_hgb_pipeline(best["params"])
    else:
        final_pipeline = build_rf_pipeline(numeric_cols, best["params"])

    final_pipeline.fit(X_final_train, y_final_train)
    test_metrics = evaluate(final_pipeline, X_test, y_test)
    print(f"Modelo final en test -> MAE={test_metrics['mae']:.2f} "
          f"RMSE={test_metrics['rmse']:.2f} R2={test_metrics['r2']:.3f}")

    with mlflow.start_run(run_name="Champion_candidate"):
        mlflow.log_param("model_type", best["model_type"])
        mlflow.log_params(best["params"])
        mlflow.log_param("random_state", 42)
        mlflow.log_param("selection_metric", "val_rmse")
        mlflow.log_param("training_strategy", "train_plus_validation")
        mlflow.log_param("test_strategy", "held_out_temporal_test")
        mlflow.log_params(common_params)

        mlflow.log_metric("test_mae", test_metrics["mae"])
        mlflow.log_metric("test_rmse", test_metrics["rmse"])
        mlflow.log_metric("test_r2", test_metrics["r2"])

        model_info = mlflow.sklearn.log_model(
            sk_model=final_pipeline,
            name="model",
            registered_model_name=MODEL_NAME,
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE
        )

    client = MlflowClient()
    client.set_registered_model_alias(MODEL_NAME, CHAMPION_ALIAS, model_info.registered_model_version)

    print(f"Champion model: {MODEL_NAME}")
    print(f"Version: {model_info.registered_model_version}")
    print(f"URI: models:/{MODEL_NAME}@{CHAMPION_ALIAS}")


if __name__ == "__main__":
    main()

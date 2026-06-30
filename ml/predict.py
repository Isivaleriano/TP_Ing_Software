import argparse
import os

import mlflow
import pandas as pd
from mlflow import MlflowClient
from sqlalchemy import create_engine
import mlflow.pyfunc

DB_URL = os.environ.get("DB_URL", "postgresql://oilgas:oilgas@localhost:5432/oilgas")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5001")
MODEL_NAME = "oil_production_forecaster"
CHAMPION_ALIAS = "Champion"

CATEGORICAL_COLS = [
    "tipopozo", "tipoextraccion", "tipoestado", "formacion", "formprod",
    "tipo_de_recurso", "sub_tipo_recurso", "clasificacion", "subclasificacion",
    "provincia", "cuenca", "areayacimiento", "areapermisoconcesion"
]

NUMERIC_COLS = [
    "prod_pet", "prod_gas", "prod_agua", "iny_agua", "iny_gas",
    "tef", "coordenadax", "coordenaday", "anio", "mes", "quarter",
    "prod_pet_lag_1", "prod_pet_lag_2", "prod_pet_lag_3", "prod_pet_lag_4",
    "prod_pet_lag_5", "prod_pet_lag_6", "prod_pet_lag_12",
    "prod_gas_lag_1", "prod_gas_lag_2", "prod_gas_lag_3", "prod_gas_lag_4",
    "prod_gas_lag_5", "prod_gas_lag_6", "prod_gas_lag_12",
    "prod_agua_lag_1", "prod_agua_lag_2", "prod_agua_lag_3",
    "prod_agua_lag_4", "prod_agua_lag_5", "prod_agua_lag_6",
    "prod_agua_lag_12"
]

FEATURE_COLS = CATEGORICAL_COLS + NUMERIC_COLS


def next_period(anio: int, mes: int) -> tuple[int, int]:
    return (anio + 1, 1) if mes == 12 else (anio, mes + 1)


def load_features(idpozo: str, anio: int, mes: int) -> pd.DataFrame:
    engine = create_engine(DB_URL)

    query = """
        SELECT *
        FROM gold.feature_store_production
        WHERE idpozo = %(idpozo)s
          AND anio = %(anio)s
          AND mes = %(mes)s
        LIMIT 1
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "idpozo": str(idpozo),
            "anio": anio,
            "mes": mes,
        },
    )

    if df.empty:
        raise ValueError(f"No features found for idpozo={idpozo}, anio={anio}, mes={mes}")

    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    return df

def load_champion():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    client = MlflowClient()
    version = client.get_model_version_by_alias(MODEL_NAME, CHAMPION_ALIAS)

    model = mlflow.pyfunc.load_model(
        f"models:/{MODEL_NAME}@{CHAMPION_ALIAS}"
    )

    return model, version


def predict_one(idpozo: str, anio: int, mes: int) -> dict:
    df = load_features(idpozo, anio, mes)
    model, version = load_champion()

    prediction = float(model.predict(df[FEATURE_COLS])[0])
    target_anio, target_mes = next_period(anio, mes)

    return {
        "idpozo": idpozo,
        "feature_anio": anio,
        "feature_mes": mes,
        "target_anio": target_anio,
        "target_mes": target_mes,
        "predicted_prod_pet": prediction,
        "model_name": MODEL_NAME,
        "model_version": version.version,
        "model_alias": CHAMPION_ALIAS,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idpozo", required=True)
    parser.add_argument("--anio", type=int, required=True)
    parser.add_argument("--mes", type=int, required=True)

    args = parser.parse_args()

    result = predict_one(
        idpozo=args.idpozo,
        anio=args.anio,
        mes=args.mes,
    )

    print(result)


if __name__ == "__main__":
    main()
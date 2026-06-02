"""Builds Silver and Gold layers from Bronze source datasets. The pipeline follows a Medallion architecture:
Bronze:
    Raw CSV files downloaded from official sources.
Silver:
    Cleaned and standardized datasets.
Gold:
    Star schema for analytical consumption.
"""

from pathlib import Path
import pandas as pd

BRONZE_DIR = Path( "data/bronze" )
SILVER_DIR = Path( "data/silver" )
GOLD_DIR = Path( "data/gold" )

TEXT_COLUMNS_PRODUCTION = [
    "idpozo",
    "idempresa",
    "empresa",
    "tipoextraccion",
    "tipoestado",
    "tipopozo",
    "provincia",
    "cuenca",
    "areayacimiento",
    "tipo_de_recurso",
]

TEXT_COLUMNS_WELLS = [
    "idpozo",
    "idempresa",
    "sigla",
    "formprod",
    "areapermisoconcesion",
    "areayacimiento",
    "cuenca",
    "provincia",
    "clasificacion",
    "subclasificacion",
    "tipo_reservorio",
    "subtipo_reservorio",
]

NUMERIC_COLUMNS_PRODUCTION = [
    "prod_pet",
    "prod_gas",
    "prod_agua",
    "iny_agua",
    "iny_gas",
    "iny_co2",
    "iny_otro",
    "tef",
]

NUMERIC_COLUMNS_WELLS = [
    "profundidad",
    "coordenadax",
    "coordenaday",
]


def clean_text_columns( df: pd.DataFrame, columns: list[str] ) -> pd.DataFrame:
    """Normalizes text columns by converting them to string and trimming spaces."""
    cleaned = df.copy()

    for column in columns:

        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype( "string" ).str.strip()

    return cleaned


def clean_numeric_columns( df: pd.DataFrame, columns: list[str], fill_value: float | None = None ) -> pd.DataFrame:
    """Converts selected columns to numeric values."""
    cleaned = df.copy()

    for column in columns:

        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric( cleaned[column], errors="coerce" )

            if fill_value is not None:
                cleaned[column] = cleaned[column].fillna( fill_value )

    return cleaned


def read_bronze() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reads raw Bronze CSV files."""
    production = pd.read_csv( BRONZE_DIR / "wells_production.csv" )
    wells = pd.read_csv( BRONZE_DIR / "listed_wells.csv" )
    return production, wells


def build_silver_production( production: pd.DataFrame ) -> pd.DataFrame:
    """Builds the cleaned production dataset. Grain is one record per well per month."""
    columns = [
        "idpozo",
        "idempresa",
        "empresa",
        "anio",
        "mes",
        "prod_pet",
        "prod_gas",
        "prod_agua",
        "iny_agua",
        "iny_gas",
        "iny_co2",
        "iny_otro",
        "tef",
        "tipoextraccion",
        "tipoestado",
        "tipopozo",
        "provincia",
        "cuenca",
        "areayacimiento",
        "tipo_de_recurso",
        "fecha_data",
    ]
    silver = production[columns].copy()
    silver = clean_text_columns( silver, TEXT_COLUMNS_PRODUCTION )
    silver = clean_numeric_columns( silver, NUMERIC_COLUMNS_PRODUCTION, fill_value=0 )
    silver["anio"] = pd.to_numeric( silver["anio"], errors="coerce" ).astype( "Int64" )
    silver["mes"] = pd.to_numeric( silver["mes"], errors="coerce" ).astype( "Int64" )
    silver["production_date"] = pd.to_datetime(
        silver["anio"].astype(str) + "-" + silver["mes"].astype(str) + "-01",
        errors="coerce",
    )
    silver = silver.drop_duplicates()
    return silver


def build_silver_wells(wells: pd.DataFrame) -> pd.DataFrame:
    """Builds the cleaned wells dataset. Grain is one record per well."""
    columns = [
        "idpozo",
        "idempresa",
        "sigla",
        "formprod",
        "profundidad",
        "areapermisoconcesion",
        "areayacimiento",
        "cuenca",
        "provincia",
        "coordenadax",
        "coordenaday",
        "clasificacion",
        "subclasificacion",
        "tipo_reservorio",
        "subtipo_reservorio",
        "fecha_data",
    ]
    silver = wells[columns].copy()
    silver = clean_text_columns( silver, TEXT_COLUMNS_WELLS )
    silver = clean_numeric_columns( silver, NUMERIC_COLUMNS_WELLS )
    silver = silver.drop_duplicates( "idpozo" )
    return silver


def build_dim_date( silver_production: pd.DataFrame ) -> pd.DataFrame:
    """Builds the date dimension from production dates."""
    dim_date = (
        silver_production[["anio", "mes", "production_date"]]
        .drop_duplicates()
        .sort_values( ["anio", "mes"] )
        .reset_index( drop=True )
    )
    dim_date.insert( 0, "date_sk", range( 1, len(dim_date) + 1 ) )
    dim_date["quarter"] = dim_date["production_date"].dt.quarter
    dim_date["semester"] = dim_date["mes"].apply( lambda month: 1 if month <= 6 else 2 )
    return dim_date


def build_dim_company( silver_production: pd.DataFrame ) -> pd.DataFrame:
    """Builds the company dimension from production records."""
    dim_company = (
        silver_production[["idempresa", "empresa"]]
        .drop_duplicates()
        .sort_values( ["idempresa", "empresa"] )
        .reset_index( drop=True )
    )
    dim_company.insert( 0, "company_sk", range( 1, len( dim_company ) + 1 ) )
    return dim_company


def build_dim_location( silver_production: pd.DataFrame ) -> pd.DataFrame:
    """Builds the location dimension. The exploratory analysis showed that provincia, cuenca and areayacimiento
    are stable for each well in the production dataset.
    """
    dim_location = (
        silver_production[["provincia", "cuenca", "areayacimiento"]]
        .drop_duplicates()
        .sort_values( ["provincia", "cuenca", "areayacimiento"] )
        .reset_index( drop=True )
    )
    dim_location.insert( 0, "location_sk", range( 1, len( dim_location ) + 1 ) )
    return dim_location


def build_dim_well( silver_production: pd.DataFrame, silver_wells: pd.DataFrame ) -> pd.DataFrame:
    """Builds the well dimension. The wells dataset is used as the main source because it has one record per well. However, production contains 
    wells that are not present in the wells catalog. Those wells are added from production to avoid losing valid production records in the Gold layer.
    """
    production_wells = silver_production[
        [
            "idpozo",
            "tipopozo",
            "tipo_de_recurso",
            "provincia",
            "cuenca",
            "areayacimiento",
        ]
    ].drop_duplicates( "idpozo" )

    dim_well = production_wells.merge(
        silver_wells[
            [
                "idpozo",
                "sigla",
                "formprod",
                "profundidad",
                "coordenadax",
                "coordenaday",
                "clasificacion",
                "subclasificacion",
                "tipo_reservorio",
                "subtipo_reservorio",
            ]
        ],
        on="idpozo",
        how="left",
    )
    dim_well["is_present_in_wells_catalog"] = dim_well["sigla"].notna()
    dim_well = dim_well.sort_values( "idpozo" ).reset_index( drop=True )
    dim_well.insert( 0, "well_sk", range( 1, len( dim_well ) + 1 ) )
    return dim_well


def build_fact_production( silver_production: pd.DataFrame, dim_well: pd.DataFrame, dim_company: pd.DataFrame, 
                          dim_location: pd.DataFrame, dim_date: pd.DataFrame ) -> pd.DataFrame:
    """Builds the production fact table.Grain is one record per well per month.The fact table is based on production records. Dimension joins are
    left joins to avoid dropping valid production records when a dimension value is incomplete or missing from the catalog."""
    fact = silver_production.merge( dim_well[["well_sk", "idpozo"]], on="idpozo", how="left" )
    fact = fact.merge( dim_company[["company_sk", "idempresa", "empresa"]], on=["idempresa", "empresa"], how="left" )
    fact = fact.merge( dim_location[["location_sk", "provincia", "cuenca", "areayacimiento"]], on=["provincia", "cuenca", "areayacimiento"], how="left" )
    fact = fact.merge( dim_date[["date_sk", "anio", "mes", "production_date"]], on=["anio", "mes", "production_date"], how="left" )
    fact_production = fact[
        [
            "well_sk",
            "company_sk",
            "location_sk",
            "date_sk",
            "idpozo",
            "anio",
            "mes",
            "prod_pet",
            "prod_gas",
            "prod_agua",
            "iny_agua",
            "iny_gas",
            "iny_co2",
            "iny_otro",
            "tef",
        ]
    ].copy()
    return fact_production


def build_gold( silver_production: pd.DataFrame, silver_wells: pd.DataFrame ) -> dict[str, pd.DataFrame]:
    """Builds Gold layer tables following a star schema."""
    dim_date = build_dim_date( silver_production )
    dim_company = build_dim_company( silver_production )
    dim_location = build_dim_location( silver_production )
    dim_well = build_dim_well( silver_production, silver_wells )
    fact_production = build_fact_production( silver_production, dim_well, dim_company, dim_location, dim_date )
    return {
        "dim_date": dim_date,
        "dim_company": dim_company,
        "dim_location": dim_location,
        "dim_well": dim_well,
        "fact_production": fact_production,
    }


def validate_gold( gold_tables: dict[str, pd.DataFrame] ) -> None:
    """Runs basic validations on Gold tables."""
    fact = gold_tables["fact_production"]

    if fact[["idpozo", "anio", "mes"]].duplicated().sum() != 0:
        raise ValueError( "fact_production grain validation failed: duplicated idpozo-anio-mes records." )

    required_keys = ["well_sk", "company_sk", "location_sk", "date_sk"]

    for key in required_keys:

        if fact[key].isna().sum() != 0:
            raise ValueError( f"fact_production contains null values in {key}." )


def main() -> None:
    """Executes Silver and Gold layer generation."""
    SILVER_DIR.mkdir( parents=True, exist_ok=True )
    GOLD_DIR.mkdir( parents=True, exist_ok=True )
    production, wells = read_bronze()
    silver_production = build_silver_production( production )
    silver_wells = build_silver_wells( wells )
    silver_production.to_csv( SILVER_DIR / "silver_wells_production.csv", index=False )
    silver_wells.to_csv( SILVER_DIR / "silver_listed_wells.csv", index=False )
    gold_tables = build_gold( silver_production, silver_wells )
    validate_gold( gold_tables )

    for table_name, table in gold_tables.items():
        output_path = GOLD_DIR / f"{table_name}.csv"
        table.to_csv( output_path, index=False )


if __name__ == "__main__":
    main()
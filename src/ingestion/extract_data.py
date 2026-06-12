"""Downloads raw source datasets into the Bronze layer."""

from pathlib import Path
import requests

BRONZE_DIR = Path( "../../data/bronze" )
DATASETS = {
    "wells_production.csv": "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv",
    "listed_wells.csv": "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/cbfa4d79-ffb3-4096-bab5-eb0dde9a8385/download/listado-de-pozos-cargados-por-empresas-operadoras.csv",
}

def download_file( url: str, output_path: Path ) -> None:
    response = requests.get( url, timeout=60 )
    response.raise_for_status()
    output_path.write_bytes( response.content )

def main() -> None:
    BRONZE_DIR.mkdir( parents=True, exist_ok=True )

    for filename, url in DATASETS.items():
        output_path = BRONZE_DIR / filename
        download_file( url, output_path )

if __name__ == "__main__":
    main()
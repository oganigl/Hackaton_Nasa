import xarray as xr
import os
import earthaccess
import requests

def download_earthdata(points, datasets, start_date, end_date):
    """
    Descarga variables específicas de múltiples datasets de EarthData para varios puntos geográficos.
    
    Args:
        points (list): Lista de dicts con {'name', 'lat', 'lon'}.
        datasets (list): Lista de tuplas (dataset_name, [variables]).
        start_date (str): Fecha inicial, formato 'YYYY-MM-DD'.
        end_date (str): Fecha final, formato 'YYYY-MM-DD'.
    """

    # Crear carpeta base
    base_folder = ".data"
    os.makedirs(base_folder, exist_ok=True)

    # Credenciales
    username = os.environ.get('EARTHDATA_USERNAME') or input("EarthData Username: ")
    password = os.environ.get('EARTHDATA_PASSWORD') or input("EarthData Password: ")
    session = requests.Session()
    session.auth = (username, password)

    # Iterar por cada dataset y sus variables
    for dataset_name, variables in datasets:
        print(f"\n🔍 Buscando dataset {dataset_name} ...")

        # Buscar granules del dataset
        results = earthaccess.search_data(
            short_name=dataset_name,
            version='5.12.4',  # Puedes cambiar la versión según el dataset
            temporal=(start_date, end_date),
            bounding_box=(-180, -90, 180, 90)
        )

        # Extraer URLs OPeNDAP
        opendap_urls = []
        for item in results:
            for urls in item['umm']['RelatedUrls']:
                if 'OPENDAP' in urls.get('Description', '').upper():
                    url = urls['URL'].replace('https', 'dap4')
                    ce = "?dap4.ce=" + "%3B".join([f"/{v}" for v in variables]) + "%3B/lat%3B/lon%3B/time"
                    opendap_urls.append(url + ce)

        if not opendap_urls:
            print(f"⚠️ No se encontraron URLs OPeNDAP para {dataset_name}")
            continue

        # Abrir con xarray
        try:
            ds = xr.open_mfdataset(opendap_urls, engine="pydap", session=session, combine='by_coords')
        except Exception as e:
            print(f"❌ Error abriendo {dataset_name}: {e}")
            continue

        # Procesar cada punto
        for point in points:
            name = point["name"]
            lat = point["lat"]
            lon = point["lon"]

            print(f"📍 Procesando punto {name} ({lat}, {lon})")

            # Crear carpeta del punto
            point_folder = os.path.join(base_folder, name)
            os.makedirs(point_folder, exist_ok=True)

            # Subconjunto más cercano al punto
            ds_point = ds.sel(lat=lat, lon=lon, method="nearest")

            # Guardar cada variable
            for var in variables:
                if var not in ds_point:
                    print(f"⚠️ Variable {var} no encontrada en {dataset_name}")
                    continue

                filename = os.path.join(point_folder, f"{dataset_name}_{var}.nc")
                ds_point[var].to_netcdf(filename)
                print(f"💾 Guardado: {filename}")

        ds.close()


# ==== Ejemplo de uso ====

if __name__ == "__main__":
    points = [
        {"name": "Valencia", "lat": 39.47, "lon": -0.38},
        {"name": "Madrid", "lat": 40.42, "lon": -3.70}
    ]

    datasets = [
        ("M2T1NXSLV", ["T2M", "U10M", "V10M"]),
        ("M2T1NXFLX", ["SLP"])
    ]

    download_earthdata(points, datasets, start_date="1980-01-01", end_date="1980-01-02")

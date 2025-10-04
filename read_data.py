import xarray as xr
import os
import earthaccess
import requests

# --- Carpeta para guardar T2M ---
data_folder = ".data"
os.makedirs(data_folder, exist_ok=True)

# --- Buscar granules en EarthData ---
results = earthaccess.search_data(
    short_name="M2T1NXSLV",
    version='5.12.4',
    temporal=('1980-01-01', '1980-01-01'),  # Ajusta la fecha según necesites
    bounding_box=(-180, 0, 180, 90)
)

# --- Extraer URLs OPeNDAP ---
opendap_urls = []
for item in results:
    for urls in item['umm']['RelatedUrls']:
        if 'OPENDAP' in urls.get('Description', '').upper():
            url = urls['URL'].replace('https', 'dap4')
            # Subset solo de variables necesarias
            ce = "?dap4.ce=/{}%3B/{}%3B/{}%3B/{}".format("T2M", "lat", "lon", "time")
            url = url + ce
            opendap_urls.append(url)

# --- Autenticación con EarthData ---
username = os.environ.get('EARTHDATA_USERNAME') or input("EarthData Username: ")
password = os.environ.get('EARTHDATA_PASSWORD') or input("EarthData Password: ")

session = requests.Session()
session.auth = (username, password)

# --- Abrir dataset con xarray y PyDAP 3.5 ---
try:
    ds = xr.open_mfdataset(
        opendap_urls,
        engine="pydap",
        session=session,
        combine='by_coords'
    )
except OSError as e:
    print("Error:", e)
    print("Revisa tus credenciales o el token/.netrc.")
    raise

# --- Subconjunto CONUS (opcional) ---
lat_min, lat_max = 25, 50
lon_min, lon_max = -125, -66
ds_conus = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

# --- Extraer solo T2M ---
t2m = ds_conus['T2M']

# --- Guardar T2M en archivos NetCDF ---
# Guardar todo en un solo archivo
all_t2m_file = os.path.join(data_folder, "T2M_all.nc")
t2m.to_netcdf(all_t2m_file)
print(f"Guardado todo T2M en: {all_t2m_file}")

# --- Guardar cada timestep por separado (opcional) ---
for i, t in enumerate(t2m.time.values):
    filename = os.path.join(data_folder, f"T2M_{i}.nc")
    t2m.isel(time=i).to_netcdf(filename)
    print(f"Guardado timestep {i}: {filename}")


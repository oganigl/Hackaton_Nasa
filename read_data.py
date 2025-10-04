#!/usr/bin/env python3
import os
from pathlib import Path
import earthaccess
import xarray as xr

# -------------------------
# Comprueba variables de entorno
# -------------------------
username = os.getenv("EARTHDATA_USERNAME")
password = os.getenv("EARTHDATA_PASSWORD")

if not username or not password:
    raise RuntimeError(
        "Define EARTHDATA_USERNAME y EARTHDATA_PASSWORD en el entorno.\n"
        "En bash: export EARTHDATA_USERNAME='tu_usuario' && export EARTHDATA_PASSWORD='tu_password'"
    )

# -------------------------
# Crear ~/.netrc seguro
# -------------------------
netrc_path = Path.home() / ".netrc"
netrc_content = f"machine urs.earthdata.nasa.gov login {username} password {password}\n"

# Escribe .netrc con permisos 600
netrc_path.write_text(netrc_content)
os.chmod(netrc_path, 0o600)

# -------------------------
# Login (earthaccess usará .netrc)
# -------------------------
auth = earthaccess.login()  # no necesita argumentos si .netrc está presente

# -------------------------
# Buscar y descargar
# -------------------------
results = earthaccess.search_data(
    short_name="M2T1NXSLV",
    version="5.12.4",
    temporal=("1980-01-01", "1980-01-01"),
    bounding_box=(-180, 0, 180, 90),
)

downloaded_files = earthaccess.download(results, local_path=".")
ds = xr.open_mfdataset(downloaded_files)
print(ds)

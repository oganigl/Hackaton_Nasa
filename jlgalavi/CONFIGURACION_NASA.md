# 🔧 Configuración NASA Earthdata

## Problemas Comunes y Soluciones

### 1. Error de Autenticación
Si recibes error de credenciales inválidas, verifica:

- **Usuario correcto**: Tu nombre de usuario NASA Earthdata
- **Contraseña correcta**: Asegúrate de usar la contraseña actual
- **Aplicaciones habilitadas**: Ve a https://urs.earthdata.nasa.gov/users/jlgalavi y habilita:
  - "NASA GES DISC DATA ARCHIVE"
  - "Hyrax in the Cloud"

### 2. Crear Archivo .netrc (Recomendado)

En tu directorio home (`C:\Users\jolug`), crea un archivo `.netrc` con:

```
machine urs.earthdata.nasa.gov
login TU_USUARIO
password TU_CONTRASEÑA
```

### 3. Alternativa: Variables de Entorno

Puedes configurar variables de entorno:
```bash
set EARTHDATA_USERNAME=tu_usuario
set EARTHDATA_PASSWORD=tu_contraseña
```

### 4. Testing con Datos Públicos

Si hay problemas de autenticación, puedes probar con datos sintéticos:

```python
from tesp_api_earthdata import interactive_download
interactive_download()  # Usa el método original
```

## URLs Útiles

- **Registro NASA Earthdata**: https://urs.earthdata.nasa.gov/
- **Aplicaciones**: https://urs.earthdata.nasa.gov/profile
- **Datos GES DISC**: https://disc.gsfc.nasa.gov/
- **Documentación earthaccess**: https://earthaccess.readthedocs.io/

## Próximos Pasos

1. **Verificar credenciales** en https://urs.earthdata.nasa.gov/
2. **Habilitar aplicaciones** necesarias
3. **Probar notebook** `nasa_earthdata_access.ipynb`
4. **Usar método requests** como fallback si es necesario

¡Una vez configurado correctamente, tendrás acceso completo a los datos NASA!
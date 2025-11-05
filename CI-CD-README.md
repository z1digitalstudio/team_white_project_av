# CI/CD Pipeline - CMS Server

## Pipeline de GitHub Actions

Este proyecto incluye un pipeline completo de CI/CD que se ejecuta automáticamente en cada push y pull request.

### Jobs del Pipeline

#### 1. **Test Job**
- ✅ Ejecuta tests unitarios con pytest
- ✅ Genera reporte de coverage
- ✅ Sube coverage a Codecov (gratuito)
- ✅ Instala dependencias del sistema (Pillow)

#### 2. **Lint Job**
- ✅ Verifica formato de código con Black
- ✅ Analiza calidad de código con Flake8
- ✅ Configuración estricta para seguridad

#### 3. **Security Job**
- ✅ Escanea código con Bandit (vulnerabilidades Python)
- ✅ Verifica dependencias con Safety
- ✅ Genera reportes de seguridad como artefactos

#### 4. **Docker Job**
- ✅ Construye imagen Docker
- ✅ Prueba que el contenedor arranca correctamente
- ✅ Verifica conectividad básica

### Herramientas de Desarrollo

#### Instalación local:
```bash
pip install -r requirements-dev.txt
```

#### Herramientas incluidas:
- **flake8**: Linting de código Python
- **black**: Formateo automático de código
- **bandit**: Escaneo de seguridad
- **safety**: Verificación de dependencias vulnerables
- **coverage**: Análisis de cobertura de tests
- **pre-commit**: Hooks de git para calidad

### Configuración

#### Archivos de configuración:
- `.flake8`: Configuración de flake8
- `.bandit`: Configuración de bandit
- `pytest.ini`: Configuración de pytest

#### Variables de entorno:
- `PYTHON_VERSION`: 3.14
- `DJANGO_SETTINGS_MODULE`: Core.settings

### Uso Local

#### Ejecutar tests:
```bash
python manage.py test
coverage run --source='.' manage.py test
coverage report
```

#### Ejecutar linting:
```bash
black --check --diff .
flake8 .
```

#### Ejecutar seguridad:
```bash
bandit -r .
safety check
```

### Estado del Pipeline

El pipeline se ejecuta en:
- Push a `main` y `develop`
- Pull requests a `main`

Puedes ver el estado en la pestaña "Actions" de GitHub.

### Próximos Pasos

1. ✅ Pipeline básico implementado
2. 🔄 Pipeline avanzado (SAST, DAST)
3. 🔄 Deployment automático
4. 🔄 Notificaciones de seguridad

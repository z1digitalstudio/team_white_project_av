# CMS Server API

Una API REST completa para gestión de blogs, posts y etiquetas con autenticación por tokens, desarrollada con Django REST Framework y documentación automática con Swagger.

## 🚀 Características

- **API REST completa** con Django REST Framework
- **Autenticación por tokens** segura
- **Documentación automática** con Swagger UI y ReDoc
- **Gestión de blogs, posts y etiquetas**
- **Permisos granulares** (público para lectura, privado para escritura)
- **Filtros y búsquedas** avanzadas
- **Tests completos** con pytest
- **Import/Export** de datos

## 📋 Requisitos

- Python 3.8+
- Django 5.2+
- SQLite3 (base de datos incluida)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/alvarovalero-z1/BlogCMSAlvaroValero.git
cd ProyectoAlvaroValero
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos SQLite3
```bash
python manage.py migrate
```

### 5. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor
```bash
python manage.py runserver
```

## 📚 Documentación de la API

### URLs de documentación
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Esquema OpenAPI**: http://localhost:8000/api/schema/

### Endpoints principales
- **API Base**: http://localhost:8000/cms/api/
- **Admin**: http://localhost:8000/admin/

## 🔐 Autenticación

La API utiliza autenticación por tokens. Para usar endpoints protegidos:

1. **Registrar usuario**:
```bash
POST /cms/api/auth/register/
{
    "username": "usuario",
    "password": "contraseña123",
    "password_confirm": "contraseña123"
}
```

2. **Iniciar sesión**:
```bash
POST /cms/api/auth/login/
{
    "username": "usuario",
    "password": "contraseña123"
}
```

3. **Usar token**:
```bash
Authorization: Token tu_token_aqui
```

## 📖 Uso de la API

### Blogs
```bash
# Listar blogs (público)
GET /cms/api/blogs/

# Crear blog (requiere autenticación)
POST /cms/api/blogs/
{
    "title": "Mi Blog",
    "description": "Descripción del blog"
}

# Obtener blog específico
GET /cms/api/blogs/{id}/

# Actualizar blog (solo propietario)
PUT /cms/api/blogs/{id}/

# Eliminar blog (solo propietario)
DELETE /cms/api/blogs/{id}/
```

### Posts
```bash
# Listar posts (público)
GET /cms/api/posts/

# Crear post (requiere autenticación)
POST /cms/api/posts/
{
    "title": "Mi Post",
    "content": "Contenido del post",
    "blog": 1,
    "tags": [1, 2]
}

# Obtener post específico
GET /cms/api/posts/{id}/

# Actualizar post (solo propietario)
PUT /cms/api/posts/{id}/

# Eliminar post (solo propietario)
DELETE /cms/api/posts/{id}/
```

### Tags
```bash
# Listar tags (público)
GET /cms/api/tags/

# Crear tag (requiere autenticación)
POST /cms/api/tags/
{
    "name": "tecnología"
}

# Obtener tag específico
GET /cms/api/tags/{id}/

# Actualizar tag
PUT /cms/api/tags/{id}/

# Eliminar tag
DELETE /cms/api/tags/{id}/
```

## 🧪 Testing

### Ejecutar tests
```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=CMSServer

# Tests específicos
pytest CMSServer/tests/tests_models.py
```

### Tests disponibles
- **tests_models.py**: Tests de modelos
- **tests_permissions.py**: Tests de permisos
- **tests_mixins.py**: Tests de mixins
- **tests_urls.py**: Tests de URLs
- **tests_utils.py**: Tests de utilidades

## 🔧 Configuración

### Variables de entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_secret_key_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
## 📦 Estructura del proyecto

```
ProyectoAlvaroValero/
├── CMSServer/                 # App principal
│   ├── models.py             # Modelos de datos
│   ├── views.py              # ViewSets con documentación
│   ├── serializers.py        # Serializers con ejemplos
│   ├── urls.py               # URLs de la API
│   ├── permissions.py        # Permisos personalizados
│   ├── mixins.py             # Mixins reutilizables
│   ├── utils.py              # Utilidades
│   └── tests/                # Tests
├── ProyectoAlvaroValero/     # Configuración del proyecto
│   ├── settings.py           # Configuración
│   └── urls.py                # URLs principales
├── db.sqlite3                # Base de datos SQLite3
├── requirements.txt           # Dependencias
├── pytest.ini               # Configuración de tests
└── README.md                # Este archivo
```

## 🚀 Despliegue

### Desarrollo
```bash
python manage.py runserver
```

### Producción
```bash
# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic

```

## 📊 Características técnicas

### Tecnologías utilizadas
- **Django 5.2**: Framework web
- **Django REST Framework 3.16**: API REST
- **drf-spectacular 0.29**: Documentación automática
- **pytest**: Testing
- **TinyMCE**: Editor de texto enriquecido
- **django-import-export**: Importación/exportación de datos

### Permisos
- **Lectura**: Pública para todos los recursos
- **Escritura**: Solo usuarios autenticados
- **Propiedad**: Solo el propietario puede editar/eliminar

### Filtros disponibles
- **Posts por blog**: `?blog=1`
- **Posts por tag**: `?tags=1,2`
- **Búsqueda**: `?search=texto`


## 👨‍💻 Autor

**Álvaro Valero**
- GitHub: [@alvarovalero-z1](https://github.com/alvarovalero-z1/BlogCMSAlvaroValero)


## 🆘 Soporte

Si tienes problemas o preguntas:

Revisa la [documentación de la API](http://localhost:8000/api/docs/)



---
# FastAPI Project 🚀

API REST con autenticación JWT, roles, middlewares personalizados y base de datos async.

## 📦 Stack

- **FastAPI** - Framework web
- **SQLAlchemy 2 (async)** - ORM con soporte async/await
- **aiosqlite** - SQLite asíncrono (fácil de cambiar a Postgres)
- **python-jose** - Tokens JWT
- **passlib + bcrypt** - Hash de contraseñas
- **pydantic-settings** - Config desde .env

## 🗂️ Estructura

```
fastapi-project/
├── app/
│   ├── main.py              # Entry point, app y middlewares
│   ├── core/
│   │   ├── config.py        # Settings desde .env
│   │   ├── database.py      # Motor async + sesión
│   │   └── security.py      # JWT, hash, dependencies
│   ├── models/
│   │   └── user.py          # Modelo SQLAlchemy
│   ├── schemas/
│   │   ├── user.py          # Pydantic schemas
│   │   └── auth.py
│   ├── routers/
│   │   ├── auth.py          # /register /login /me
│   │   ├── users.py         # CRUD usuarios
│   │   └── items.py         # Resource de ejemplo
│   ├── services/
│   │   └── user_service.py  # Lógica de negocio
│   └── middlewares/
│       ├── logging_middleware.py   # Log de requests
│       └── rate_limit.py          # Rate limiter por IP
├── tests/
│   └── test_auth.py
├── .env
└── requirements.txt
```

## 🚀 Levantar el proyecto

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar servidor
uvicorn app.main:app --reload

# 4. Abrir docs
# http://localhost:8000/docs
```

## 🔐 Auth

El usuario admin por defecto se crea automáticamente al iniciar:

| Campo    | Valor      |
|----------|------------|
| username | admin      |
| password | admin1234  |
| role     | admin      |

### Flujo de autenticación

1. `POST /api/v1/auth/register` → crear cuenta
2. `POST /api/v1/auth/login` → obtener JWT
3. Usar el token en el header: `Authorization: Bearer <token>`

## 🛡️ Roles

| Rol   | Permisos                                     |
|-------|----------------------------------------------|
| user  | Ver y editar su propio perfil, gestionar sus items |
| admin | Todo lo anterior + ver/editar/eliminar todos  |

## 🔌 Endpoints principales

```
GET  /health
GET  /docs

POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me

GET  /api/v1/users/              (admin)
GET  /api/v1/users/{id}
PATCH /api/v1/users/{id}
PATCH /api/v1/users/{id}/admin   (admin)
DELETE /api/v1/users/{id}        (admin)

GET  /api/v1/items/
POST /api/v1/items/
GET  /api/v1/items/{id}
DELETE /api/v1/items/{id}
```

## 🧪 Tests

```bash
pytest tests/ -v
```

## ⚙️ Variables de entorno (.env)

```env
SECRET_KEY=tu-clave-secreta-muy-larga
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite+aiosqlite:///./app.db
ALLOWED_ORIGINS=["http://localhost:3000"]
```

---

> Próximo paso: Dockerizar y subir a producción 🐳

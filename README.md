![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

#### Здесь приведен один из вариантов создания базового приложения на языке программирования Python использование таких инструментов как:
- FastAPI - это быстрый (высокопроизводительный) веб-фреймворк для создания API с Python на основе стандартных подсказок типов Python.
- Uvicorn — это реализация веб-сервера ASGI для Python.
- Pydantic — наиболее широко используемая библиотека проверки данных для Python.
- SQLAlchemy — это популярная библиотека для работы с базами данных в Python. Она предоставляет инструменты для выполнения SQL-запросов, управления соединениями и использования ORM (Object-Relational Mapping) — подхода, который позволяет работать с базами данных через Python-классы, вместо написания SQL-запросов вручную.

1. ### Установка зависимостей pip install: 
- fastapi, uvicorn, pydantic, SQLAlchemy

2. ### Создание main.py
```python
import uvicorn
from fastapi import FastAPI

app = FastAPI()  # создание приложения 

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, workers=3)
```
> - автоматический запуск сервера \
```python
uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, workers=3)
```

### 3. Для работы с базой данных нужно создать ее для этого создаем database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_URL = "sqlite:///sql_app.db"
engine = create_engine(SQLALCHEMY_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
> - наша бд и ее место нахождение \
  SQLALCHEMY_URL = "sqlite:///sql_app.db" 
> - движок с помощью которого будет работать наша бд \
> engine = create_engine(SQLALCHEMY_URL, connect_args={"check_same_thread": False})
> - фабрика сессий для выполнения операций с бд \
> SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
> - базовый клас для всех моделей и таблиц в бд \
> Base = declarative_base()
> - функция get_db для управления сессиями базы данных в SQLAlchemy \
> - 
### 4. Создание модели для приложения. 
>  Создаем директорию models и в ней файл user.py где:
```python
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users" # название таблицы

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
```

### 5. Создаем директорию dto с файлом user.py (фильтрования поступающих данных)
> DTO (Data Transfer Object) — это объект, который используется для передачи данных между 
> различными частями приложения или между сервисами. 
> DTO часто применяют в ситуациях, где нужно минимизировать объём передаваемой 
> информации и отделить внутренние структуры данных от внешнего взаимодействия.
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
```
> pydantic используется для валидации данных
> 
### 6. Пишем сервис для работы с базой данных через нашу модель
> сервис CRUD пишем в отдельной директории services в файле user.py
```python
from models.user import User  # Импорт модели базы данных. Эта модель описывает таблицу
from sqlalchemy.orm import Session  # Импорт объекта сессии. используется для взаимодействия с базой данных.
from dto import user  # DTO, который обеспечивает передачу только необходимых данных.

# Создание пользователя
def create_user(data: user.User, db: Session):
    """
    Аргументы:
    data: DTO, содержащий данные пользователя (например, name).
    db: объект сессии для взаимодействия с базой данных.
    Что делает:
    1. Создаёт экземпляр модели User, заполняя его данными из DTO.
    2. Добавляет нового пользователя в сессию с помощью db.add(user).
    3. Сохраняет изменения в базе данных с помощью db.commit().
    4. Обновляет объект user после сохранения (например, заполняет его сгенерированным id).
    5. Возвращает созданного пользователя.
    """
    user = User(name=data.name)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        print(e)
    return user

# Получение пользователя
def get_user(id: int, db):
    """
    Аргументы:
    id: идентификатор пользователя, которого нужно получить.
    db: объект сессии.
    Что делает:
    1. Выполняет запрос к базе данных для поиска пользователя с указанным id.
    2. Использует метод filter для фильтрации пользователей.
    3. Возвращает первого найденного пользователя с помощью first()
    """
    return db.query(User).filter(User.id == id).first()

# Обновление пользователя
def update(id: int, data: user.User, db: Session):
    """
    Аргументы:
    id: идентификатор пользователя, которого нужно получить.
    data: DTO, содержащий данные пользователя
    db: объект сессии.
    Что делает:
    1. Находит пользователя в базе данных по id.
    2. Обновляет его имя (user.name = data.name).
    3. Добавляет обновлённого пользователя в сессию с помощью db.add(user).
    4. Сохраняет изменения в базе данных (db.commit()).
    5. Обновляет объект user, чтобы отразить изменения.
    6. Возвращает обновлённого пользователя.
    """
    user = db.query(User).filter(User.id == id).first()
    user.name = data.name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Удаление пользователя
def remove(id: int, db: Session):
    """
    Аргументы:
    id: идентификатор пользователя для удаления.
    db: объект сессии.
    Что делает:
    1. Выполняет запрос для поиска пользователя с указанным id.
    2. Удаляет найденного пользователя с помощью метода delete().
    3. Возвращает результат удаления (например, количество удалённых записей).
    """
    user = db.query(User).filter(User.id == id).delete()
    return user
```
> Этот код реализует набор функций для выполнения CRUD-операций 
> (создание, чтение, обновление, удаление) с использованием SQLAlchemy. 
> Эти операции применяются к модели User, описанной в файле models.user, 
> и используют DTO (Data Transfer Object) для передачи данных.

### 7. Создание контролера в папке routers в файле main.py
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from services import user as UserService
from dto import user as UserDTO


router = APIRouter()  # Инструмент FastAPI для создания модульных маршрутов, позволяет сгруппировать все маршруты


# Создание пользователя
@router.post("/", tags=["user"])  # POST для создания ресурса; Маршрут: /
async def create(data: UserDTO.User = None, db: Session = Depends(get_db)):
    """
    Аргументы:
    data: UserDTO.User: Данные пользователя (DTO).
    db: Session: Объект сессии, переданный через Depends(get_db).
    Что делает:
    Передаёт данные и объект сессии в метод create_user из UserService, 
    который добавляет пользователя в базу данных.
    Результат: 
    Возвращает созданного пользователя.
    """
    return UserService.create_user(data, db)


# Получение пользователя
@router.get("/{id}", tags=["user"])  # GET для получения данных; Маршрут: /{id} (где {id} — идентификатор пользователя).
async def get(id: int, db: Session = Depends(get_db)):
    """
    Аргументы:
    id: int: Идентификатор пользователя.
    db: Session: Объект сессии.
    Что делает:
    Вызывает get_user из UserService, чтобы найти пользователя в базе данных.
    Результат: 
    Возвращает данные пользователя.
    """
    return UserService.get_user(id, db)


# Обновление данных пользователя
@router.put("/{id}", tags=["user"])  # PUT для обновления ресурса; Маршрут: /{id}
async def update(id: int, data:UserDTO.User = None, db: Session = Depends(get_db)):
    """
    Аргументы:
    id: int: Идентификатор пользователя.
    data: UserDTO.User: Новые данные пользователя.
    db: Session: Объект сессии.
    Что делает:
    Обновляет данные пользователя с указанным id в методе update из UserService.
    Результат: 
    Возвращает обновлённого пользователя.
    """
    return UserService.update(id, data, db)


# Удаление данных пользователя
@router.delete("/{id}", tags=["user"])  # DELETE для удаления ресурса; Маршрут: /{id}
async def delete(id: int, db: Session = Depends(get_db)):
    """
    Аргументы:
    id: int: Идентификатор пользователя.
    db: Session: Объект сессии.
    Что делает:
    Удаляет пользователя с указанным id через метод remove из UserService.
    Результат: 
    Возвращает результат операции.
    """
    return UserService.remove(id, db)
```
> - Этот код представляет собой модуль в FastAPI для работы с сущностью User. 
> Он использует APIRouter для группировки маршрутов (endpoints), 
> предоставляя CRUD-функционал: создание, чтение, обновление и удаление.

- Каждый маршрут имеет тег tags=["user"], который помогает:
- - Группировать связанные маршруты в документации (например, Swagger UI).
- - Улучшить читаемость документации.

### 8. Соединяем наши API с нашим приложением
> Соединение будет производится в main.py
> Для этого рассмотрим наш код
```python
import uvicorn  # Сервер ASGI, который используется для запуска приложения FastAPI.
from fastapi import FastAPI  # Фреймворк для создания веб-приложений.
from database import Base, SessionLocal, engine  # элементы для управления базой данных (создание таблиц, подключение).
from routers import user as UserRouter  # Импорт маршрутизатора для работы с пользователями.

Base.metadata.create_all(bind=engine)  # # Создаём таблицы в базе данных, если их нет то они будут созданы автоматически.
app = FastAPI()  # Экземпляр FastAPI, для настройки маршрутов, обработки запросов и управления приложением.
app.include_router(UserRouter.router, prefix="/user")  # include_router: Подключает маршрутизатор

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, workers=3)
```
- Итоговый процесс
- - Создаётся и настраивается база данных.
- - Инициализируется приложение FastAPI.
- - Добавляются маршруты с префиксом /user.
- - Запускается сервер Uvicorn для обслуживания приложения.

#### Некоторые пояснения:
> user.py имя файлов в различных директориях. Однообразие имени служит для того,
> чтобы в дальнейшем понять к какому объекту приложения принадлежит тот или иной сервис.

> В FastAPI такие понятия, как контроллеры, ручки и роутеры, 
> относятся к разным уровням организации кода, 
> но иногда эти термины могут использоваться взаимозаменяемо. 
> Давайте разберём различия и их роли:

#### 1. Контроллеры (Controllers)
>Что это:
- Контроллеры — это концептуальный уровень, который организует логику обработки запросов. 
Они обычно представляют функциональность, связанную с определённым ресурсом 
или модулем приложения.

>В FastAPI:
В самом FastAPI термин "контроллеры" не используется напрямую, 
> но вы можете создать Python-классы, которые будут выполнять роль контроллеров, 
> группируя методы для обработки запросов.
- Пример:
```python
class UserController:
    def get_user(self, user_id: int):
        # Логика получения пользователя
        return {"user_id": user_id}
```
#### 2. Ручки (Handlers)
>Что это:
- Ручка (handler) — это конкретная функция, которая обрабатывает определённый HTTP-запрос.
Ручка обычно отвечает за один конкретный маршрут (например, GET /users).\

>В FastAPI:
Это отдельная функция, связанная с маршрутом с помощью декоратора 
> (@app.get, @app.post и т.д.).
- Пример:
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```
#### 3. Роутеры (Routers)
>Что это:
Роутеры — это инструмент для группировки маршрутов (routes) в FastAPI. 
> Они помогают разделить приложение на модули и упрощают организацию кода.

>В FastAPI:
Роутеры реализуются с помощью объекта APIRouter, 
> который объединяет несколько маршрутов в одном месте.
Это особенно полезно для модульного подхода, 
> где каждый роутер отвечает за свою часть приложения.
- Пример:
```python
from fastapi import APIRouter

user_router = APIRouter()

@user_router.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

app.include_router(user_router)
```
>Итог \
-Контроллеры: концептуальная организация логики (возможно, реализуется вручную). \
-Ручки: функции, привязанные к маршрутам. \
-Роутеры: инструмент FastAPI для группировки маршрутов.




1. ### установка зависимостей pip install: 
- fastapi, uvicorn, pydantic, SQLAlchemy

2. ### создание main.py
```python
import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, workers=3)
```
> - автоматический запуск сервера \
>    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, workers=3)
>   создание приложения 
> - app = FastAPI()

3. ### для работы с базой данных нужно создать ее для этого создаем database.py
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
4. ### создание модели для приложения. 
>  Создаем директорию models и в ней файл user.py где:
```python
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users" # название таблицы

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
```
5. ### Создаем директорию dto с файлом user.py фильтрования поступающих данных
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
6. ### Пишем сервис для работы с базой данных через нашу модель
> сервис CRUD пишем в отдельной директории services в файле user.py
```pytohn
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


### некоторые пояснения:
> user.py имя файлов в различных директориях. Однообразие имени служит для того,
> чтобы в дальнейшем понять к какому объекту приложения принадлежит тот или иной сервис.



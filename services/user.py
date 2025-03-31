from models.user import User
from sqlalchemy.orm import Session
from dto import user


def create_user(data: user.User, db: Session):
    user = User(name=data.name)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        print(e)
    return user


def get_user(id: int, db):
    return db.query(User).filter(User.id == id).first()


def get_users_all(db):
    return db.query(User).all()


def update(id: int, data: user.User, db: Session):
    user = db.query(User).filter(User.id == id).first()
    user.name = data.name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def remove(id: int, db: Session):
    user = db.query(User).filter(User.id == id).delete()
    return user

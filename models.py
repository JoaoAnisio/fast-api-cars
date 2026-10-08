from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy_utils.types import ChoiceType

#criação da conexão com o banco de dados SQLite
db = create_engine("sqlite:///database.db")

#criação da base de dados
Base = declarative_base()

#criação das tabelas/classes do banco de dados
class user(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    admin = Column(Boolean, default=False) 

    def __init__(self, name: str, email: str, password: str, active: bool = True, admin: bool = False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin


class car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    color = Column(String, nullable=False)
    mileage = Column(Integer, nullable=False)

    def __init__(self, make: str, model: str, year: int, price: float, color: str, mileage: int):
        self.make = make
        self.model = model
        self.year = year
        self.price = price
        self.color = color
        self.mileage = mileage

class order(Base):
    __tablename__ = "orders"

    """ status_order = [
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED'),
        ('CANCELED', 'CANCELED')
    ] """

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    status = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)   

    def __init__(self, user_id: int, car_id: int, price: float, status='PENDING'):
        self.user_id = user_id
        self.car_id = car_id
        self.price = price
        self.status = status
        self.order_date = datetime.utcnow()


#criação das tabelas no banco de dados
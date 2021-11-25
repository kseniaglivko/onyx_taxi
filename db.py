"""Модуль для создания и работы с базой данных."""
from contextlib import contextmanager
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    create_engine,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy_utils.types.choice import ChoiceType
from typing import Generator
from datetime import datetime

engine = create_engine("postgresql://dbuser:dbpassword@localhost/db")

Base = declarative_base()

Session = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=engine))


@contextmanager
def session_manager() -> Generator:
    """Создание сессий для осуществления запросов к БД.."""
    session = Session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Order(Base):  # type: ignore
    """Класс, описывающий таблицу БД с заказами."""

    __tablename__ = "orders"  # название таблицы.
    client = relationship("Client")
    driver = relationship("Driver")

    STATUS_TYPES = {
        "not_accepted": "not_accepted",
        "in_progress": "in_progress",
        "done": "done",
        "cancelled": "cancelled",
    }

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(Integer, autoincrement=True, primary_key=True, comment="Идентификатор заказа")
    address_from = Column(String, nullable=False, comment="Адрес отправления")
    address_to = Column(String, nullable=False, comment="Адрес назначения")
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    date_created = Column(
        DateTime, default=datetime.utcnow, comment="Дата создания заказа"
    )
    status = Column(
        ChoiceType(STATUS_TYPES, impl=String()), nullable=False, comment="Статус заказа",
    )

    def __init__(
            self,
            id: str = None,
            address_from: str = None,
            address_to: str = None,
            client_id: str = None,
            driver_id: str = None,
            date_created: str = None,
            status: str = None,
    ) -> None:
        """Инициализация заказа."""
        self.id = id
        self.address_to = address_from
        self.address_from = address_to
        self.client_id = client_id
        self.driver_id = driver_id
        self.date_created = date_created
        self.status = status

    def __repr__(self) -> str:
        """Переопределение метода print."""
        return str(
            {
                "order_id": self.id,
                "address_from": self.address_from,
                "address_to": self.address_to,
                "client_id": self.client_id,
                "driver_id": self.driver_id,
                "date_created": self.date_created.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                "status": str(self.status),
            }
        )

    @staticmethod
    def get_order_info(order_id: str) -> str:
        """SELECT-запрос по номеру заказа."""
        with session_manager() as session:
            info = session.query(Order).get(int(order_id))
            return info

    @staticmethod
    def get_order_status(order_id: str) -> str:
        """SELECT-запрос о статусе заказа по его номеру."""
        with session_manager() as session:
            info = session.query(Order.status).filter(Order.id == int(order_id)).first()
            return info

    def create_order(self) -> None:
        """Создание заказа."""
        with session_manager() as session:
            session.add(self)
            session.commit()

    @staticmethod
    def update_order_status(order_id: str, new_status: str) -> None:
        """Изменение статуса заказа."""
        with session_manager() as session:
            session.query(Order).filter(Order.id == int(order_id)).update(
                {Order.status: new_status}
            )
            session.commit()

    @staticmethod
    def update_order(
            order_id: str, new_client_id: str, new_driver_id: str, new_status: str
    ) -> None:
        """Изменение информации о заказе."""
        with session_manager() as session:
            session.query(Order).filter(Order.id == int(order_id)).update(
                {
                    Order.client_id: int(new_client_id),
                    Order.driver_id: int(new_driver_id),
                    Order.status: new_status,
                }
            )
            session.commit()


class Client(Base):  # type: ignore
    """Класс, описывающий таблицу БД с данными клиентов."""

    __tablename__ = "clients"  # название таблицы.

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(Integer, autoincrement=True, primary_key=True, comment="Идентификатор клиента")
    name = Column(String, nullable=False, comment="Имя клиента")
    is_vip = Column(Boolean, nullable=False, comment="Статус клиента")

    def __init__(self, id: int = None, name: str = None, is_vip: bool = None) -> None:
        """Инициализация клиента."""
        self.id = id
        self.name = name
        self.is_vip = is_vip

    def __repr__(self) -> str:
        """Переопределение метода print."""
        return str({"id": self.id, "name": self.name, "is_vip": self.is_vip})

    @staticmethod
    def get_client_info(client_id: str) -> str:
        """SELECT-запрос по id клиента."""
        with session_manager() as session:
            info = session.query(Client).get(int(client_id))
            return info

    def create_client(self) -> None:
        """Создание клиента."""
        with session_manager() as session:
            session.add(self)
            session.commit()

    @staticmethod
    def delete_client(client_id: str) -> None:
        """Удаление записи о клиенте."""
        with session_manager() as session:
            session.query(Client).filter(Client.id == int(client_id)).delete()
            session.commit()


class Driver(Base):  # type: ignore
    """Класс, описывающий таблицу БД с данными водителей."""

    __tablename__ = "drivers"  # название таблицы.

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(Integer, autoincrement=True, primary_key=True, comment="Идентификатор водителя")
    name = Column(String, nullable=False, comment="Имя водителя")
    car = Column(String, nullable=False, comment="Название машины")

    def __init__(self, id: int = None, name: str = None, car: str = None) -> None:
        """Инициализация водителя."""
        self.id = id
        self.name = name
        self.car = car

    def __repr__(self) -> str:
        """Переопределение метода print."""
        return str({"id": self.id, "name": self.name, "car": self.car})

    @staticmethod
    def get_driver_info(driver_id: str) -> str:
        """SELECT-запрос по id водителя."""
        with session_manager() as session:
            info = session.query(Driver).get(int(driver_id))
            return info

    def create_driver(self) -> None:
        """Создание клиента."""
        with session_manager() as session:
            session.add(self)
            session.commit()

    @staticmethod
    def delete_driver(driver_id: str) -> None:
        """Удаление записи о клиенте."""
        with session_manager() as session:
            session.query(Driver).filter(Driver.id == int(driver_id)).delete()
            session.commit()


Base.metadata.create_all(engine)

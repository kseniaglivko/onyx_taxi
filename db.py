"""Модуль для создания и работы с базой данных."""
import enum
from contextlib import contextmanager
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    create_engine,
    ForeignKey,
    Sequence,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.sql import func
from sqlalchemy_utils.types.choice import ChoiceType
from typing import Generator

engine = create_engine("postgresql://dbuser:dbpassword@localhost/db")

Base = declarative_base()

Session = scoped_session(sessionmaker(ind=engine))


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


class OrderStatus(enum.Enum):
    """Варианты статусов заказа."""

    not_accepted = "not_accepted"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class Order(Base):  # type: ignore
    """Класс, описывающий таблицу БД с заказами."""

    __tablename__ = "orders"  # название таблицы.
    client = relationship("Client", back_populates="orders")
    driver = relationship("Driver", back_populates="orders")

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(
        Integer,
        Sequence("order_id_seq", start=1001, increment=1),
        primary_key=True,
        comment="Идентификатор заказа",
    )
    address_from = Column(String, nullable=False, comment="Адрес отправления")
    address_to = Column(String, nullable=False, comment="Адрес назначения")
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    date_created = Column(
        DateTime, server_default=func.now(), comment="Дата создания заказа"
    )
    status = Column(
        ChoiceType(OrderStatus, impl=String()), nullable=False, comment="Статус заказа",
    )

    def __init__(
        self,
        address_from: str = None,
        address_to: str = None,
        client_id: str = None,
        driver_id: str = None,
        status: str = None,
    ) -> None:
        """Инициализация заказа."""
        self.address_to = address_from
        self.address_from = address_to
        self.client_id = client_id
        self.driver_id = driver_id
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
                "status": self.status,
            }
        )

    @staticmethod
    def get_order_info(order_id: str) -> str:
        """SELECT-запрос по номеру заказа."""
        with session_manager() as session:
            info = session.query(Order).get(int(order_id))
            return info

    @staticmethod
    def create_order() -> None:
        """Создание заказа."""
        with session_manager() as session:
            session.add()
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
    orders = relationship("Order", back_populates="Client")

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(
        Integer,
        Sequence("client_id_seq", start=2001, increment=1),
        primary_key=True,
        comment="Идентификатор клиента",
    )
    name = Column(String, nullable=False, comment="Имя клиента")
    is_vip = Column(Boolean, nullable=False, comment="Статус клиента")

    def __init__(self, name: str = None, is_vip: bool = None) -> None:
        """Инициализация клиента."""
        self.name = name
        self.is_vip = is_vip

    def __repr__(self) -> str:
        """Переопределение метода print."""
        return str({"id": self.id, "name": self.name, "is_vip": self.is_vip})

    @staticmethod
    def get_client_info(client_id: str) -> str:
        """SELECT-запрос по id клиента."""
        with session_manager() as session:
            info = session.query(Order).get(int(client_id))
            return info

    @staticmethod
    def create_client() -> None:
        """Создание клиента."""
        with session_manager() as session:
            session.add()
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
    orders = relationship("Order", back_populates="Client")

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(
        Integer,
        Sequence("driver_id_seq", start=3001, increment=1),
        primary_key=True,
        comment="Идентификатор водителя",
    )
    name = Column(String, nullable=False, comment="Имя водителя")
    car = Column(String, nullable=False, comment="Название машины")

    def __init__(self, name: str = None, car: str = None) -> None:
        """Инициализация водителя."""
        self.name = name
        self.car = car

    def __repr__(self) -> str:
        """Переопределение метода print."""
        return str({"id": self.id, "name": self.name, "car": self.car})

    @staticmethod
    def get_driver_info(driver_id: str) -> str:
        """SELECT-запрос по id водителя."""
        with session_manager() as session:
            info = session.query(Order).get(int(driver_id))
            return info

    @staticmethod
    def create_driver() -> None:
        """Создание клиента."""
        with session_manager() as session:
            session.add()
            session.commit()

    @staticmethod
    def delete_driver(driver_id: str) -> None:
        """Удаление записи о клиенте."""
        with session_manager() as session:
            session.query(Client).filter(Client.id == int(driver_id)).delete()
            session.commit()


Base.metadata.create_all(engine)

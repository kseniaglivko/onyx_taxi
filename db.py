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
from sqlalchemy.sql.functions import sysdate
from sqlalchemy_utils.types.choice import ChoiceType
from typing import Generator

engine = create_engine("postgresql://dbuser:dbpassword@localhost:8080/db")

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


class Order(Base):
    """Класс, описывающий таблицу БД с заказами."""

    __tablename__ = "orders"  # название таблицы.
    client = relationship("Client")
    driver = relationship("Driver")

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="Идентификатор заказа"
    )
    address_from = Column(String, nullable=False, comment="Адрес отправления")
    address_to = Column(String, nullable=False, comment="Адрес назначения")
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    date_created = Column(
        DateTime, default=sysdate, nullable=False, comment="Дата создания заказа"
    )
    status = Column(
        ChoiceType(
            ["not_accepted", "in_progress", "done", "in_progress"], impl=String()
        ),
        nullable=False,
        comment="Статус заказа",
    )

    def __repr__(self):
        """Переопределение метода print."""
        return (
            f"Заказ № {self.id} с {self.address_from} до {self.address_to}, создан {self.date_created}. "
            f"Статус - {self.status}. "
            f"Идентификатор клиента - {self.client_id}, идентификатор водителя - {self.driver_id}. "
        )

    @staticmethod
    def get_order_info(order_id: int) -> str:
        """SELECT-запрос по номеру заказа."""
        with session_manager() as session:
            info = session.query(Order).filter(Order.id == order_id).all()
            return info

    @staticmethod
    def create_order(
        address_from: str, address_to: str, client_id: int, driver_id: int, status: str
    ) -> None:
        """Создание заказа."""
        with session_manager() as session:
            session.add(
                Order(
                    address_from=address_from,
                    address_to=address_to,
                    client_id=client_id,
                    driver_id=driver_id,
                    date_created=sysdate,
                    status=status,
                )
            )
            session.commit()

    @staticmethod
    def update_order_status(order_id, new_status) -> None:
        """Изменение статуса заказа."""
        with session_manager() as session:
            session.query(Order).filter(Order.id == order_id).update(
                {Order.status: new_status}
            )
            session.commit()

    @staticmethod
    def update_order(
        order_id: int, new_client_id: int, new_driver_id: int, new_status: str
    ) -> None:
        """Изменение информации о заказе."""
        with session_manager() as session:
            session.query(Order).filter(Order.id == order_id).update(
                {
                    Order.client_id: new_client_id,
                    Order.driver_id: new_driver_id,
                    Order.date_created: sysdate,
                    Order.status: new_status,
                }
            )
            session.commit()


class Client(Base):
    """Класс, описывающий таблицу БД с данными клиентов."""

    __tablename__ = "clients"  # название таблицы.

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="Идентификатор клиента"
    )
    name = Column(String, nullable=False, comment="Имя клиента")
    is_vip = Column(Boolean, nullable=False, comment="Статус клиента")

    def __repr__(self):
        """Переопределение метода print."""
        return f"Клиент {self.name}. Идентификатор клиента - {self.id}, vip-статус - {self.is_vip}."

    @staticmethod
    def get_client_info(client_id: int) -> str:
        """SELECT-запрос по id клиента."""
        with session_manager() as session:
            info = session.query(Client).filter(Client.id == client_id).all()
            return info

    @staticmethod
    def create_client(name: str, is_vip: bool) -> None:
        """Создание клиента."""
        with session_manager() as session:
            session.add(Client(name=name, is_vip=is_vip))
            session.commit()

    @staticmethod
    def delete_client(client_id: int) -> None:
        """Удаление записи о клиенте."""
        with session_manager() as session:
            session.delete(Client).filter(Client.id == client_id)
            session.commit()


class Driver(Base):
    """Класс, описывающий таблицу БД с данными водителей."""

    __tablename__ = "drivers"  # название таблицы.

    # Атрибуты класса, описывающие колонки таблицы, их типы данных и ограничения.
    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="Идентификатор водителя"
    )
    name = Column(String, nullable=False, comment="Имя водителя")
    car = Column(String, nullable=False, comment="Название машины")

    def __repr__(self):
        """Переопределение метода print."""
        return f"Водитель {self.name}. Идентификатор водителя - {self.id}, машина - {self.car}."

    @staticmethod
    def get_driver_info(driver_id: int) -> str:
        """SELECT-запрос по id водителя."""
        with session_manager() as session:
            info = session.query(Driver).filter(Driver.id == driver_id).all()
            return info

    @staticmethod
    def create_driver(name: str, car: str) -> None:
        """Создание клиента."""
        with session_manager() as session:
            session.add(Driver(name=name, car=car))
            session.commit()

    @staticmethod
    def delete_driver(driver_id: int) -> None:
        """Удаление записи о клиенте."""
        with session_manager() as session:
            session.delete(Driver).filter(Driver.id == driver_id)
            session.commit()


Base.metadata.create_all(engine)

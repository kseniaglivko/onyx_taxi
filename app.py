"""Реализация взаимодействия с базой данных через API."""
from flask import Flask, Response, request
from typing import Any

from db import Driver, Client, Order

app = Flask(__name__)


@app.route("/")
def index() -> str:
    """Вывод приветствия на главной странице."""
    return "Welcome to Onyx.Taxi!"


@app.route("/drivers/<driver_id>", methods=["GET"])
def find_driver(driver_id: str) -> Any:
    """Поиск водителя по id."""
    driver = Driver()
    try:
        response = driver.get_driver_info(driver_id)
        if response is None:
            return Response("Объект в базе не найден.", status=404)
        return str(response)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/drivers/<driver_id>", methods=["DELETE"])
def delete_driver(driver_id: str) -> Response:
    """Удаление водителя из системы."""
    driver = Driver()
    try:
        response = driver.get_driver_info(driver_id)
        if response is None:
            return Response("Объект в базе не найден.", status=404)
        driver.delete_driver(driver_id)
        return Response("Удалено.", status=201)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/drivers", methods=["POST"])
def create_driver() -> Response:
    """Создание записи о водителе."""
    driver_info = request.get_json()
    try:
        driver = Driver(id=driver_info["id"], name=driver_info["name"], car=driver_info["car"])
        driver.create_driver()
        return Response("Запись создана.", status=201)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/clients/<client_id>", methods=["GET"])
def find_client(client_id: str) -> Any:
    """Поиск клиента по id."""
    client = Client()
    try:
        response = client.get_client_info(client_id)
        if response is None:
            return Response("Объект в базе не найден.", status=404)
        return str(response)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/clients/<client_id>", methods=["DELETE"])
def delete_client(client_id: str) -> Response:
    """Удаление клиента из системы."""
    client = Client()
    try:
        response = client.get_client_info(client_id)
        if response is None:
            return Response("Объект в базе не найден.", status=404)
        client.delete_client(client_id)
        return Response("Удалено.", status=201)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/clients", methods=["POST"])
def create_client() -> Response:
    """Создание записи о клиенте."""
    client_info = request.get_json()
    try:
        client = Client(id=client_info["id"], name=client_info["name"], is_vip=client_info["is_vip"])
        client.create_client()
        return Response("Запись создана.", status=201)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/orders/<order_id>", methods=["GET"])
def find_order(order_id: str) -> Any:
    """Поиск заказа по id."""
    order = Order
    try:
        response = order.get_order_info(order_id)
        if response is None:
            return Response("Объект в базе не найден.", status=404)
        return str(response)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/orders", methods=["POST"])
def create_order() -> Response:
    """Создание заказа."""
    order_info = request.get_json()
    try:
        order = Order(
            id=order_info["id"],
            address_from=order_info["address_from"],
            address_to=order_info["address_to"],
            client_id=order_info["client_id"],
            driver_id=order_info["driver_id"],
            date_created=order_info["date_created"],
            status=order_info["status"],
        )
        order.create_order()
        return Response("Запись создана.", status=201)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/orders/<order_id>", methods=["PUT"])
def update_order(order_id: str) -> Response:
    """Изменение заказа."""
    order = Order()
    try:
        new_order_data = request.get_json()
        if order.get_order_info(order_id) is None:
            return Response("Объект в базе не найден.", status=404)
        order_status = order.get_order_status(order_id)
        if (
            new_order_data["status"] in ["in_progress", "cancelled"]
            and "not_accepted" in order_status
        ):
            try:
                order.update_order(
                    order_id,
                    new_order_data["client_id"],
                    new_order_data["driver_id"],
                    new_order_data["status"],
                )
                return Response("Запись изменена.", status=201)
            except Exception:
                return Response("Неправильный запрос.", status=400)
        elif (
            new_order_data["status"] in ["done", "cancelled"]
            and "in_progress" in order_status
        ):
            try:
                order.update_order_status(order_id, new_order_data["status"])
                return Response("Запись изменена.", status=201)
            except Exception:
                return Response("Неправильный запрос.", status=400)
        return Response("Неверная последовательность статусов", status=400)
    except Exception:
        return Response("Плохой json.", status=400)

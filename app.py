"""Реализация взаимодействия с базой данных через API."""

from flask import Flask, Response, json, request
from typing import Any
import ast
from db import Driver, Client, Order

app = Flask("onyx_taxi")


@app.route("/drivers/<int:id>", methods=["GET"])
def find_driver(driver_id: int) -> Any:
    """Поиск водителя по id."""
    driver = Driver()
    try:
        response = driver.get_driver_info(driver_id)
        if response == "":
            return Response("Объект в базе не найден.", status=404)
        return response
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/drivers/<int:id>", methods=["DELETE"])
def delete_driver(driver_id: int) -> Response:
    """Удаление водителя из системы."""
    driver = Driver()
    try:
        if str(driver.get_driver_info(driver_id)) == "":
            return Response("Объект в базе не найден.", status=404)
        driver.delete_driver(driver_id)
        return Response("Удалено.", status=204)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/drivers", methods=["POST"])
def create_driver() -> Response:
    """Создание записи о водителе."""
    driver = Driver()
    try:
        data = json.loads(request.data.decode("utf-8"))
        driver.create_driver(data["name"], data["car"])
        return Response("Запись создана.", status=204)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/clients/<int:id>", methods=["GET"])
def find_client(client_id: int) -> Any:
    """Поиск клиента по id."""
    client = Client()
    try:
        response = client.get_client_info(client_id)
        if response == "":
            return Response("Объект в базе не найден.", status=404)
        return response
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/clients/<int:id>", methods=["DELETE"])
def delete_client(client_id: int) -> Response:
    """Удаление клиента из системы."""
    client = Client()
    try:
        if str(client.get_client_info(client_id)) == "":
            return Response("Объект в базе не найден.", status=404)
        client.delete_client(client_id)
        return Response("Удалено.", status=204)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/clients", methods=["POST"])
def create_client() -> Response:
    """Создание записи о клиенте."""
    client = Client()
    try:
        data = json.loads(request.data.decode("utf-8"))
        client.create_client(data["name"], data["is_vip"])
        return Response("Запись создана.", status=204)
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/orders/<int:id>", methods=["GET"])
def find_order(order_id: int) -> Any:
    """Поиск заказа по id."""
    order = Order()
    try:
        response = order.get_order_info(order_id)
        if response == "":
            return Response("Объект в базе не найден.", status=404)
        return response
    except Exception:
        return Response("Неправильный запрос.", status=400)


@app.route("/orders", methods=["POST"])
def create_order() -> Response:
    """Создание заказа."""
    order = Order()
    try:
        data = json.loads(request.data.decode("utf-8"))
        try:
            order.create_order(
                data["address_from"],
                data["address_to"],
                data["client_id"],
                data["driver_id"],
                data["status"],
            )
            return Response("Запись создана.", status=204)
        except Exception:
            return Response("Неправильный запрос.", status=400)
    except Exception:
        return Response("Плохой json.", status=400)


@app.route("/orders/<int:id>", methods=["PUT"])
def update_order(order_id: int) -> Response:
    """Изменение заказа."""
    order = Order()
    try:
        data = json.loads(request.data.decode("utf-8"))
        if order.get_order_info(order_id) == "":
            return Response("Объект в базе не найден.", status=404)
        db_data = order.get_order_info(order_id)
        order_status = ast.literal_eval(db_data)
        if (
            data["status"] in ["in_progress", "cancelled"]
            and order_status["status"] == "not_accepted"
        ):
            try:
                order.update_order(
                    order_id, data["client_id"], data["driver_id"], data["status"],
                )
                return Response("Запись изменена.", status=204)
            except Exception:
                return Response("Неправильный запрос.", status=400)
        elif (
            data["status"] in ["done", "cancelled"]
            and order_status["status"] == "in_progress"
        ):
            try:
                order.update_order_status(
                    order_id, data["status"],
                )
                return Response("Запись изменена.", status=204)
            except Exception:
                return Response("Неправильный запрос.", status=400)
    except Exception:
        return Response("Плохой json.", status=400)

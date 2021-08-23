"""Реализация взаимодействия с базой данных через API."""

from flask import Flask, Response, json, request
from typing import Any
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


@app.route("/drivers/<int:id>", methods=["POST"])
def create_driver() -> Response:
    """Изменение информации о водителе."""
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


@app.route("/clients/<int:id>", methods=["POST"])
def create_client() -> Response:
    """Изменение информации о клиенте."""
    client = Client()
    try:
        data = json.loads(request.data.decode("utf-8"))
        client.create_client(data["name"], data["is_vip"])
        return Response("Запись создана.", status=204)
    except Exception:
        return Response("Неправильный запрос.", status=400)

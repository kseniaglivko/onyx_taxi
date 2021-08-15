from sqlalchemy import create_engine, Column, String, Table, MetaData
from sqlalchemy_utils.types.choice import ChoiceType
from typing import List
import databases
from fastapi import FastAPI
from pydantic import BaseModel

DATABASE_URL = "postgresql://dbuser:dbpassword@postgresserver/db"
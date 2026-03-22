# -*- coding: utf-8 -*-
from abc import ABC
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine

__all__ = ["EnginePSQL", "EngineSQLite"]


class Engine(ABC):

    __name__ == "Engine"

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._engine = None


class EnginePSQL(Engine):
    """Union all custom sql requests."""

    __name__ = "EnginePSQL"

    def __init__(
        self,
        username,
        password,
        host,
        service_name,
        async_req,
        connect_args=None,
        port=None,
        driver="postgresql",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._driver = driver
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._service_name = service_name
        self._connect_args = connect_args if connect_args else {}
        self._async_req = async_req
        self._url = (
            f"{self._driver}{'+asyncpg' if self._async_req else ''}://{self._username}:"
            + f"{self._password}@{self._host}:"
            + f"{self._port}/{self._service_name}"
        )
        self.__create_engine()

    def __create_engine(self) -> None:

        func = create_async_engine if self._async_req else create_engine
        self._engine = func(
            self._url, connect_args=self._connect_args, poolclass=pool.NullPool
        )


class EngineSQLite(Engine):
    """Union all custom sql requests."""

    __name__ = "EngineSQLite"

    def __init__(
        self,
        file_path,
        connect_args=None,
        **kwargs,
    ):
        super().__init__(file_path=file_path)
        self.connect_args = connect_args if connect_args else {}
        self.url = f"sqlite+aiosqlite:///{file_path}"
        self.__create_engine(**kwargs)

    def __create_engine(self, **kwargs) -> None:

        self._engine = create_async_engine(
            self.url,
            connect_args=self.connect_args,
            poolclass=pool.NullPool,
            **kwargs,
        )

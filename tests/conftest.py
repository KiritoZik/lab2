from logging import Logger
from unittest.mock import Mock
import pytest
from typing import cast
from pytest_mock import MockerFixture
from src.services.luckyos_console import LuckyOSConsoleService


"""
Fixture — это функция, которая подготавливает контекст для теста:
создаёт объект, настраивает окружение, делает моки, создает временные файлы и т.п.

Фикстура вызывается автоматически, достаточно просто указать её имя в параметрах теста.
"""


@pytest.fixture
def logger(mocker: MockerFixture) -> Logger:
    return cast(Logger, mocker.Mock())


@pytest.fixture
def service(logger: Logger):
    return LuckyOSConsoleService(logger)


@pytest.fixture
def fake_pathlib_path_class(mocker: MockerFixture) -> Mock:
    return cast(Mock, mocker.patch("src.services.luckyos_console.Path"))

from pathlib import Path
from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture

from src.services.base import OSConsoleServiceBase


def test_cd_for_nonexisted_directory(
    service: OSConsoleServiceBase, fake_pathlib_path_class: Mock, mocker: MockerFixture
):
    """Тест cd для несуществующей директории"""
    fake_path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    fake_path_object.exists.return_value = False
    nonexistent_path: str = "/nonexistent"
    fake_pathlib_path_class.return_value = fake_path_object

    with pytest.raises(FileNotFoundError):
        service.cd(nonexistent_path)


def test_cd_for_file(
    service: OSConsoleServiceBase,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):
    """Тест cd для файла (не директории)"""
    path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_object.exists.return_value = True
    path_object.is_dir.return_value = False
    not_a_directory_file: str = "file.txt"
    fake_pathlib_path_class.return_value = path_object

    with pytest.raises(NotADirectoryError):
        service.cd(not_a_directory_file)


def test_cd_for_parent_directory(
    service: OSConsoleServiceBase,
    mocker: MockerFixture,
):
    """Тест cd для .. (родительская директория)"""
    current_path = Path("/current")
    parent_path_obj = mocker.create_autospec(Path, instance=True, spec_set=True)
    parent_path_obj.exists.return_value = True
    parent_path_obj.is_dir.return_value = True

    mocker.patch("src.services.luckyos_console.Path.cwd", return_value=current_path)
    mocker.patch("src.services.luckyos_console.access", return_value=True)
    mock_chdir = mocker.patch("src.services.luckyos_console.os.chdir")

    service.cd("..")

    mock_chdir.assert_called_once()


def test_cd_for_home_directory(
    service: OSConsoleServiceBase,
    mocker: MockerFixture,
):
    """Тест cd для ~ (домашняя директория)"""
    home_path_obj = mocker.create_autospec(Path, instance=True, spec_set=True)
    home_path_obj.exists.return_value = True
    home_path_obj.is_dir.return_value = True

    mocker.patch("src.services.luckyos_console.Path.cwd", return_value=Path("/current"))
    mocker.patch("src.services.luckyos_console.Path.home", return_value=home_path_obj)
    mocker.patch("src.services.luckyos_console.access", return_value=True)
    mock_chdir = mocker.patch("src.services.luckyos_console.os.chdir")

    service.cd("~")

    mock_chdir.assert_called_once()


def test_cd_permission_denied(
    service: OSConsoleServiceBase,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):
    """Тест cd для директории без прав доступа"""
    path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_object.exists.return_value = True
    path_object.is_dir.return_value = True
    fake_pathlib_path_class.return_value = path_object
    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.cd("/restricted")


def test_cd_os_error(
    service: OSConsoleServiceBase,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):
    """Тест cd для случая когда os.chdir вызывает OSError"""
    path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_object.exists.return_value = True
    path_object.is_dir.return_value = True
    fake_pathlib_path_class.return_value = path_object
    mocker.patch("src.services.luckyos_console.access", return_value=True)
    mocker.patch("src.services.luckyos_console.os.chdir", side_effect=OSError("Cannot change directory"))

    with pytest.raises(OSError):
        service.cd("/some/path")

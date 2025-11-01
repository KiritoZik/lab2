import os.path
from pathlib import Path
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from src.services.base import OSConsoleServiceBase


def test_rm_file(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест rm для удаления файла"""
    fs.create_dir("data")
    file_path = os.path.join("data", "file.txt")
    fs.create_file(file_path, contents="test")

    mock_remove = mocker.patch("src.services.luckyos_console.remove")

    service.rm(file_path, False)

    mock_remove.assert_called_once()


def test_rm_directory_without_recursive(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест rm для директории без опции -r (должна быть ошибка)"""
    fs.create_dir("data")

    with pytest.raises(FileNotFoundError):
        service.rm("data", False)


def test_rm_directory_with_recursive(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест rm для удаления директории с опцией -r"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")

    mocker.patch("src.services.luckyos_console.typer.prompt", return_value="y")
    mock_rmtree = mocker.patch("src.services.luckyos_console.shutil.rmtree")

    service.rm("data", True)

    mock_rmtree.assert_called_once()


def test_rm_parent_directory_forbidden(service: OSConsoleServiceBase, mocker: MockerFixture):
    """Тест rm для запрета удаления родительской директории"""
    current_path = Path("/current")
    parent_path = Path("/")

    mocker.patch("pathlib.Path.cwd", return_value=current_path)

    path_mock = mocker.Mock(spec=Path)
    path_mock.__eq__ = lambda self, other: str(self) == str(other)
    path_mock.__str__ = lambda self: str(parent_path)
    mocker.patch("src.services.luckyos_console.Path", return_value=path_mock)

    path_mock.exists.return_value = True
    path_mock.is_dir.return_value = True
    path_mock.parent = parent_path

    # Act & Assert
    with pytest.raises(IsADirectoryError):
        service.rm(parent_path, True)


def test_rm_root_directory_forbidden(service: OSConsoleServiceBase, mocker: MockerFixture):
    """Тест rm для запрета удаления корневой директории"""
    current_path = Path("/current")
    root_path = Path("/")

    mocker.patch("pathlib.Path.cwd", return_value=current_path)

    path_mock = mocker.Mock(spec=Path)
    path_mock.__eq__ = lambda self, other: str(self) == str(other) or (hasattr(other, 'anchor') and str(self) == other.anchor)
    path_mock.__str__ = lambda self: str(root_path)
    mocker.patch("src.services.luckyos_console.Path", return_value=path_mock)

    path_mock.exists.return_value = True
    path_mock.is_dir.return_value = True
    path_mock.parent = root_path

    with pytest.raises(IsADirectoryError):
        service.rm(root_path, True)


def test_rm_directory_not_confirmed(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест rm для случая когда пользователь не подтверждает удаление"""
    fs.create_dir("data")

    mocker.patch("src.services.luckyos_console.typer.prompt", return_value="n")
    mock_rmtree = mocker.patch("src.services.luckyos_console.shutil.rmtree")

    service.rm("data", True)

    mock_rmtree.assert_not_called()


def test_rm_directory_os_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест rm для случая когда shutil.rmtree вызывает OSError"""
    fs.create_dir("data")

    mocker.patch("src.services.luckyos_console.typer.prompt", return_value="y")
    mocker.patch("src.services.luckyos_console.shutil.rmtree", side_effect=OSError("Delete failed"))

    with pytest.raises(OSError):
        service.rm("data", True)


def test_rm_file_os_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест rm для случая когда os.remove вызывает OSError"""
    fs.create_file("file.txt", contents="test")

    mocker.patch("src.services.luckyos_console.remove", side_effect=OSError("Delete failed"))

    with pytest.raises(OSError):
        service.rm("file.txt", False)


def test_rm_file_permission_denied(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест rm для файла без прав доступа"""
    fs.create_file("file.txt", contents="test")
    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.rm("file.txt", False)


def test_rm_directory_permission_denied(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест rm для директории без прав доступа"""
    fs.create_dir("data")
    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.rm("data", True)


def test_rm_file_not_found_error(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест rm для несуществующего файла"""

    with pytest.raises(FileNotFoundError):
        service.rm("nonexistent.txt", False)

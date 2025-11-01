import os.path
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from src.services.base import OSConsoleServiceBase


def test_mv_for_nonexisted_file(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест mv для несуществующего файла"""
    fs.create_dir("dest")

    mocker.patch("src.services.luckyos_console.access", return_value=True)

    with pytest.raises(FileNotFoundError):
        service.mv("nonexistent.txt", "dest/")


def test_mv_file_to_directory(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест mv для перемещения файла"""
    fs.create_dir("data")
    fs.create_dir("dest")
    content = "test content"
    source_file = os.path.join("data", "source.txt")
    fs.create_file(source_file, contents=content)

    mock_move = mocker.patch("src.services.luckyos_console.shutil.move")

    service.mv(source_file, "dest/")

    mock_move.assert_called_once()


def test_mv_permission_denied_source(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест mv для файла без прав доступа на чтение"""
    fs.create_file("source.txt", contents="test")
    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.mv("source.txt", "dest/")


def test_mv_permission_denied_destination(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест mv для случая когда destination существует но недоступен"""
    fs.create_file("source.txt", contents="test")
    fs.create_dir("dest")

    def access_side_effect(path, mode):
        if str(path) == "source.txt":
            return True
        return False  # dest недоступен

    mocker.patch("src.services.luckyos_console.access", side_effect=access_side_effect)

    with pytest.raises(PermissionError):
        service.mv("source.txt", "dest/")


def test_mv_os_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест mv для случая когда shutil.move вызывает OSError"""
    fs.create_file("source.txt", contents="test")
    fs.create_dir("dest")
    mocker.patch("src.services.luckyos_console.access", return_value=True)
    mocker.patch("src.services.luckyos_console.shutil.move", side_effect=OSError("Move failed"))

    with pytest.raises(OSError):
        service.mv("source.txt", "dest/")

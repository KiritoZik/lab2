import os.path
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

from src.services.base import OSConsoleServiceBase


def test_cp_for_nonexisted_file(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cp для несуществующего файла"""
    fs.create_dir("data")
    fs.create_dir("dest")

    with pytest.raises(FileNotFoundError):
        service.cp("nonexistent.txt", "dest/", False)


def test_cp_file_to_directory(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест cp для копирования файла в директорию"""
    fs.create_dir("data")
    fs.create_dir("dest")
    content = "test content"
    source_file = os.path.join("data", "source.txt")
    fs.create_file(source_file, contents=content)

    mock_copy2 = mocker.patch("src.services.luckyos_console.shutil.copy2")

    service.cp(source_file, "dest/", False)

    mock_copy2.assert_called_once()


def test_cp_directory_without_recursive(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cp для директории без опции -r (должна быть ошибка)"""
    fs.create_dir("data")
    fs.create_dir("dest")

    with pytest.raises(IsADirectoryError):
        service.cp("data", "dest/", False)


def test_cp_directory_with_recursive(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест cp для копирования директории с опцией -r"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")
    fs.create_dir("dest")

    mock_copytree = mocker.patch("src.services.luckyos_console.shutil.copytree")

    service.cp("data", "dest/", True)

    mock_copytree.assert_called_once()


def test_cp_os_error_file(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест cp для случая когда shutil.copy2 вызывает OSError"""
    fs.create_file("source.txt", contents="test")
    fs.create_dir("dest")

    mocker.patch("src.services.luckyos_console.shutil.copy2", side_effect=OSError("Copy failed"))

    with pytest.raises(OSError):
        service.cp("source.txt", "dest/", False)


def test_cp_os_error_directory(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест cp для случая когда shutil.copytree вызывает OSError"""
    fs.create_dir("data")
    fs.create_dir("dest")

    mocker.patch("src.services.luckyos_console.shutil.copytree", side_effect=OSError("Copy failed"))

    with pytest.raises(OSError):
        service.cp("data", "dest/", True)


def test_cp_file_is_dir_error(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cp для случая когда файл является директорией без -r"""
    fs.create_dir("data")

    with pytest.raises(IsADirectoryError):
        service.cp("data", "dest/", False)


def test_cp_recursive_not_directory(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cp для случая когда с -r передается файл"""
    fs.create_file("source.txt", contents="test")

    with pytest.raises(IsADirectoryError):
        service.cp("source.txt", "dest/", True)

import os.path
import tarfile
import pytest
from pytest_mock import MockerFixture
from pyfakefs.fake_filesystem import FakeFilesystem
from src.services.base import OSConsoleServiceBase


def test_tar_for_nonexisted_folder(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест tar для несуществующей директории"""
    fs.create_dir("dest")

    with pytest.raises(FileNotFoundError):
        service.tar("nonexistent", "archive.tar.gz")


def test_tar_directory(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест tar для архивирования директории"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")
    archive_path = "archive.tar.gz"

    service.tar("data", archive_path)

    assert os.path.exists(archive_path)


def test_untar_for_nonexisted_file(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест untar для несуществующего файла"""
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        service.untar("nonexistent.tar.gz")


def test_tar_permission_denied(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест tar для директории без прав доступа"""
    fs.create_dir("data")
    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.tar("data", "archive.tar.gz")


def test_tar_os_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест tar для случая когда создание архива вызывает OSError"""
    fs.create_dir("data")
    mocker.patch("src.services.luckyos_console.tarfile.open", side_effect=OSError("Tar creation failed"))

    with pytest.raises(OSError):
        service.tar("data", "archive.tar.gz")


def test_untar_permission_denied(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест untar для файла без прав доступа"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")

    archive_path = "archive.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add("data", arcname="data")

    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.untar(archive_path)


def test_untar_os_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест untar для случая когда распаковка вызывает OSError"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")

    archive_path = "archive.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add("data", arcname="data")

    mock_tar = mocker.Mock()
    mock_tar.extractall.side_effect = OSError("Extract failed")
    mock_tar_context = mocker.Mock()
    mock_tar_context.__enter__ = mocker.Mock(return_value=mock_tar)
    mock_tar_context.__exit__ = mocker.Mock(return_value=None)
    mocker.patch("src.services.luckyos_console.tarfile.open", return_value=mock_tar_context)

    with pytest.raises(OSError):
        service.untar(archive_path)

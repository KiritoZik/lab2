import os.path
import zipfile
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from src.services.base import OSConsoleServiceBase


def test_zip_for_nonexisted_folder(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест zip для несуществующей директории"""
    fs.create_dir("dest")

    with pytest.raises(FileNotFoundError):
        service.zip("nonexistent", "archive.zip")


def test_zip_for_file(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест zip для файла (не директории)"""
    fs.create_file("file.txt", contents="test")

    with pytest.raises(NotADirectoryError):
        service.zip("file.txt", "archive.zip")


def test_zip_directory(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест zip для архивирования директории"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")
    archive_path = "archive.zip"

    service.zip("data", archive_path)

    assert os.path.exists(archive_path)
    assert zipfile.is_zipfile(archive_path)


def test_unzip_for_nonexisted_file(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест unzip для несуществующего файла"""
    with pytest.raises(FileNotFoundError):
        service.unzip("nonexistent.zip")


def test_unzip_for_non_zip_file(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест unzip для файла, который не является zip архивом"""
    fs.create_file("not_zip.txt", contents="not a zip")

    from src.errors import NotAZipFileError
    with pytest.raises(NotAZipFileError):
        service.unzip("not_zip.txt")


def test_zip_permission_denied(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест zip для директории без прав доступа"""
    fs.create_dir("data")
    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.zip("data", "archive.zip")


def test_zip_os_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест zip для случая когда создание архива вызывает OSError"""
    fs.create_dir("data")
    mocker.patch("src.services.luckyos_console.zipfile.ZipFile", side_effect=OSError("Zip creation failed"))

    with pytest.raises(OSError):
        service.zip("data", "archive.zip")


def test_unzip_permission_denied(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест unzip для файла без прав доступа"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")

    import zipfile
    archive_path = "archive.zip"
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.write(os.path.join("data", "file.txt"))

    mocker.patch("src.services.luckyos_console.access", return_value=False)

    with pytest.raises(PermissionError):
        service.unzip(archive_path)


def test_unzip_os_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест unzip для случая когда распаковка вызывает OSError"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "file.txt"), contents="test")

    import zipfile
    archive_path = "archive.zip"
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.write(os.path.join("data", "file.txt"))

    mock_zipfile = mocker.patch("src.services.luckyos_console.zipfile")
    mock_zipfile.is_zipfile.return_value = True
    mock_zip_context = mocker.Mock()
    mock_zip_context.__enter__ = mocker.Mock(return_value=mock_zip_context)
    mock_zip_context.__exit__ = mocker.Mock(return_value=None)
    mock_zip_context.extractall.side_effect = OSError("Extract failed")
    mock_zipfile.ZipFile.return_value = mock_zip_context

    with pytest.raises(OSError):
        service.unzip(archive_path)

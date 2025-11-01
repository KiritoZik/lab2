import os.path
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from src.services.base import OSConsoleServiceBase


def test_cat_for_nonexisted_file(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cat для несуществующего файла"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "existing.txt"), contents="test")

    with pytest.raises(FileNotFoundError):
        service.cat(filename=os.path.join("data", "nonexisting.txt"))


def test_cat_for_folder(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cat для директории (должна быть ошибка)"""
    fs.create_dir("data")
    fs.create_file(os.path.join("data", "existing.txt"), contents="test")

    with pytest.raises(IsADirectoryError):
        service.cat("data")


def test_cat_file_with_text(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cat для существующего файла"""
    fs.create_dir("data")
    content = "test content"
    path = os.path.join("data", "existing.txt")
    fs.create_file(path, contents=content)

    result = service.cat(path)

    assert result == content


def test_cat_file_with_multiline_text(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест cat для файла с несколькими строками"""
    fs.create_dir("data")
    content = "line 1\nline 2\nline 3"
    path = os.path.join("data", "multiline.txt")
    fs.create_file(path, contents=content)

    result = service.cat(path)

    assert result == content


def test_cat_read_error(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест cat для случая когда чтение файла вызывает OSError"""
    fs.create_file("file.txt", contents="test")

    mock_path = mocker.patch("src.services.luckyos_console.Path")
    mock_path_instance = mocker.Mock()
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_dir.return_value = False
    mock_path_instance.read_text.side_effect = OSError("Cannot read file")
    mock_path.return_value = mock_path_instance

    with pytest.raises(OSError):
        service.cat("file.txt")

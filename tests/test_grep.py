import os.path
import pytest
from pytest_mock import MockerFixture
from pyfakefs.fake_filesystem import FakeFilesystem
from src.services.base import OSConsoleServiceBase


def test_grep_for_nonexisted_path(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест grep для несуществующего пути"""
    with pytest.raises(FileNotFoundError):
        service.grep("pattern", "nonexistent.txt", False, False)


def test_grep_in_file(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест grep для поиска в файле"""
    fs.create_dir("data")
    file_path = os.path.join("data", "file.txt")
    fs.create_file(file_path, contents="test pattern here\nanother line")

    result = service.grep("pattern", file_path, False, False)

    assert len(result) == 1
    assert result[0][0] == file_path
    assert result[0][1] == 1  # номер строки
    assert "pattern" in result[0][2]  # совпадение


def test_grep_recursive(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест grep для рекурсивного поиска"""
    fs.create_dir("data")
    fs.create_dir(os.path.join("data", "subdir"))
    fs.create_file(os.path.join("data", "file1.txt"), contents="pattern found")
    fs.create_file(os.path.join("data", "subdir", "file2.txt"), contents="pattern here")

    result = service.grep("pattern", "data", True, False)

    assert len(result) >= 2


def test_grep_ignore_case(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест grep с опцией игнорирования регистра"""
    fs.create_dir("data")
    file_path = os.path.join("data", "file.txt")
    fs.create_file(file_path, contents="TEST Pattern HERE")

    result = service.grep("pattern", file_path, False, True)

    assert len(result) >= 1


def test_grep_invalid_pattern(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест grep для невалидного регулярного выражения"""
    fs.create_dir("data")
    file_path = os.path.join("data", "file.txt")
    fs.create_file(file_path, contents="test")

    with pytest.raises(OSError):
        service.grep("[invalid", file_path, False, False)


def test_grep_multiple_matches(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест grep для нескольких совпадений в одном файле"""
    fs.create_dir("data")
    file_path = os.path.join("data", "file.txt")
    fs.create_file(file_path, contents="pattern line 1\nno match\npattern line 2")

    result = service.grep("pattern", file_path, False, False)

    assert len(result) == 2


def test_grep_empty_directory(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест grep для пустой директории"""
    fs.create_dir("empty_dir")

    result = service.grep("pattern", "empty_dir", False, False)

    assert result == []


def test_grep_os_error_reading_file(service: OSConsoleServiceBase, fs: FakeFilesystem, mocker: MockerFixture):
    """Тест grep для случая когда чтение файла вызывает OSError"""
    fs.create_dir("data")
    file_path = os.path.join("data", "file.txt")
    fs.create_file(file_path, contents="test pattern")

    mocker.patch("src.services.luckyos_console.open", side_effect=OSError("Cannot read file"), create=True)

    with pytest.raises(OSError):
        service.grep("pattern", file_path, False, False)

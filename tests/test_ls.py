from pathlib import Path
from unittest.mock import Mock
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

from src.services.base import OSConsoleServiceBase


def test_ls_for_nonexisted_folder(
    service: OSConsoleServiceBase, fake_pathlib_path_class: Mock, mocker: MockerFixture
):
    """Тест ls для несуществующей директории"""
    fake_path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    fake_path_object.exists.return_value = False
    nonexistent_path: str = "/nonexistent"
    fake_pathlib_path_class.return_value = fake_path_object

    with pytest.raises(FileNotFoundError):
        service.ls(nonexistent_path, False)

    fake_pathlib_path_class.assert_called_with(nonexistent_path)
    fake_path_object.exists.assert_called_once()


def test_ls_for_file(
    service: OSConsoleServiceBase,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):
    """Тест ls для файла (не директории)"""
    path_object: Mock = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_object.exists.return_value = True
    path_object.is_dir.return_value = False
    not_a_directory_file: str = "file.txt"
    fake_pathlib_path_class.return_value = path_object

    with pytest.raises(NotADirectoryError):
        service.ls(not_a_directory_file, False)

    fake_pathlib_path_class.assert_called_with(not_a_directory_file)
    path_object.exists.assert_called_once()


def test_ls_for_existing_directory(
    service: OSConsoleServiceBase,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):
    """Тест ls для существующей директории без опции -l"""
    path_obj = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_obj.exists.return_value = True
    path_obj.is_dir.return_value = True

    entry = mocker.Mock()
    entry.name = "file.txt"
    path_obj.iterdir.return_value = [entry]

    fake_pathlib_path_class.return_value = path_obj

    result = service.ls("/fake/dir", False)

    fake_pathlib_path_class.assert_called_once_with("/fake/dir")
    path_obj.exists.assert_called_once_with()
    path_obj.is_dir.assert_called_once_with()
    path_obj.iterdir.assert_called_once_with()
    assert result == ["file.txt\n"]


def test_ls_long_format(
    service: OSConsoleServiceBase,
    fake_pathlib_path_class: Mock,
    mocker: MockerFixture,
):
    """Тест ls для директории с опцией -l"""
    import datetime
    import stat

    path_obj = mocker.create_autospec(Path, instance=True, spec_set=True)
    path_obj.exists.return_value = True
    path_obj.is_dir.return_value = True

    entry = mocker.Mock()
    entry.name = "file.txt"
    file_info = mocker.Mock()
    file_info.st_mode = stat.S_IFREG | 0o644
    file_info.st_nlink = 1
    file_info.st_size = 100
    file_info.st_mtime = datetime.datetime.now().timestamp()
    entry.stat.return_value = file_info

    path_obj.iterdir.return_value = [entry]
    fake_pathlib_path_class.return_value = path_obj

    result = service.ls("/fake/dir", True)

    assert len(result) == 1
    assert len(result[0]) == 5  # права, ссылки, размер, дата, имя
    assert result[0][4] == "file.txt"
    entry.stat.assert_called_once()


def test_ls_empty_directory(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест ls для пустой директории"""
    fs.create_dir("empty_dir")

    result = service.ls("empty_dir", False)

    assert result == []


def test_ls_empty_directory_long(service: OSConsoleServiceBase, fs: FakeFilesystem):
    """Тест ls для пустой директории с опцией -l"""
    fs.create_dir("empty_dir")

    result = service.ls("empty_dir", True)

    assert result == []

import datetime
import shutil
import stat
import os
import zipfile
import tarfile
import re
from logging import Logger
from os import PathLike, access, R_OK, remove
from pathlib import Path
import typer
from src.services.base import OSConsoleServiceBase
from src.errors import NotAZipFileError


class LuckyOSConsoleService(OSConsoleServiceBase):
    def __init__(self, logger: Logger):
        self._logger = logger
    def ls(self, path: PathLike[str] | str, long: bool) -> list[str] | list[list[object]]:
        path = Path(path)
        if not path.exists():
            self._logger.error(f"Папка на найдена: {path}")
            raise FileNotFoundError(path)
        if not path.is_dir():
            self._logger.error(f"Введенный путь {path} не является директорией")
            raise NotADirectoryError(path)
        self._logger.info(f"Чтение {path}")
        if long:
            entry = []
            for file in path.iterdir():
                file_info = file.stat()
                type_and_access = stat.filemode(file_info.st_mode)
                count_link = file_info.st_nlink
                size_file = file_info.st_size
                change_date = datetime.datetime.fromtimestamp(
                        file_info.st_mtime).strftime("%b %d %H:%M")
                entry.append([type_and_access, count_link, size_file, change_date, file.name])
            return entry
        else:
            return [entry.name + "\n" for entry in path.iterdir()]


    def cd(self, path: PathLike[str] | str) -> None:
        if str(path) == "..":
            path = Path.cwd().parent
        elif str(path) == "~":
            path = Path.home()
        else:
            path = Path(path)
        if not path.exists():
            self._logger.error(f"Директория не найдена: {path}")
            raise FileNotFoundError(path)
        if not path.is_dir():
            self._logger.error(f"Введенный путь {path} не является директорией")
            raise NotADirectoryError(path)
        if not access(path, R_OK):
            self._logger.error(f"Отказано в доступе: {path}")
            raise PermissionError(path)
        try:
            os.chdir(path)
            self._logger.info(f"Директория изменена на {path}")
        except OSError as e:
            self._logger.error(e)
            raise e


    def cat(self, filename: PathLike[str] | str) -> str:
        path = Path(filename)
        if not path.exists():
            self._logger.error(f"Файл не найден: {filename}")
            raise FileNotFoundError(filename)
        if path.is_dir():
            self._logger.error(f"Введенный путь {filename} не является файлом")
            raise IsADirectoryError(f"Введенный путь {filename} не является файлом")
        try:
            self._logger.info(f"Чтение файла {filename} ")
            return path.read_text(encoding="utf-8")
        except OSError:
            self._logger.exception(f"Ошибка чтения {filename}")
            raise


    def cp(self,
           filename: PathLike[str] | str,
           dct: PathLike[str] | str,
           recursive: bool) -> None:
        dct = Path(dct)
        filename  = Path(filename)
        dct.parent.mkdir(parents=True, exist_ok=True)
        if not filename.exists():
            self._logger.error(f"Директория или файлы не найдены: {filename}")
            raise FileNotFoundError(f"Директория или файлы не найдены: {filename}")
        if  not recursive:
            if filename.is_dir():
                raise IsADirectoryError(f"{filename} директория, используйте --recursive, что скопировать ее")
            try:
                shutil.copy2(filename, dct)
                self._logger.info(f"{filename} скопировано в {dct}")
            except OSError:
                self._logger.exception(f"Ошибка копирования {filename} в {dct}")
                raise OSError(f"Ошибка копирования {filename} в {dct}")
        else:
            if not filename.is_dir():
                self._logger.error(f"Введенный путь {filename} не является директорией")
                raise IsADirectoryError(f"Введенный путь {filename} не является директорией")
            try:
                shutil.copytree(filename, dct, dirs_exist_ok=True)
                self._logger.info(f"{filename} скопировано с рекурсией в {dct}")
            except OSError:
                self._logger.exception(f"Ошибка копирования {filename} в {dct}")
                raise OSError(f"Ошибка копирования {filename} в {dct}")


    def mv(
            self,
            path1: PathLike[str] | str,
            path2: PathLike[str] | str,
    ) -> None:
        path1 = Path(path1)
        path2 = Path(path2)
        if not access(path1, R_OK):
            self._logger.error(f"Введенный путь {path1} недоступен для чтения")
            raise PermissionError(f"Введенный путь {path1} недоступен для чтения")
        if not path1.exists():
            self._logger.error(f"Папка или директория не найдена: {path1}")
            raise FileNotFoundError(path1)
        if path2.exists() and not access(path2, R_OK):
            self._logger.error(f"Введенный путь {path2} недоступен для чтения")
            raise PermissionError(f"Введенный путь {path2} недоступен для чтения")
        try:
            shutil.move(path1, path2)
            self._logger.info(f"Перемещено {path1} -> {path2}")
        except OSError:
            self._logger.exception(f"Ошибка перемещения {path1} в {path2}")
            raise OSError(f"Ошибка перемещения {path1} в {path2}")



    def rm(self, path: PathLike[str] | str, recursive: bool) -> None:
        path = Path(path)
        if recursive:
            path_now = Path.cwd()
            if path == path_now.parent:
                self._logger.error(f"Введенный путь {path_now} является родительской директорией")
                raise IsADirectoryError(f"Введенный путь {path_now} является родительской директорией")
            if path == Path(path_now.anchor):
                self._logger.error(f"Введенный путь {path_now} является корневой директорией")
                raise IsADirectoryError(f"Введенный путь {path_now} является корневой директорией")
            if not path.is_dir():
                self._logger.error(f"Введенный путь {path} не является директорией")
                raise NotADirectoryError(path)
            if not path.exists():
                self._logger.error(f"Директория не найдена: {path}")
                raise FileNotFoundError(path)
            if not access(path, R_OK):
                self._logger.error(f"Введенный путь {path} недоступен для чтения")
                raise PermissionError(f"Введенный путь {path} недоступен для чтения")
            try:
                conf = typer.prompt("Подтвердите удаление директории [y/n]")
                if conf == "y":
                    shutil.rmtree(path)
                    self._logger.info(f"Удалено {path}")
            except OSError:
                self._logger.exception(f"Ошибка удаления {path}")
                raise OSError(f"Ошибка удаления {path}")

        else:
            if not path.is_file():
                self._logger.error(f"Файл не найден: {path}")
                raise FileNotFoundError(path)
            if not path.exists():
                self._logger.error(f"Папка не найдена: {path}")
                raise FileExistsError(path)
            if not access(path, R_OK):
                self._logger.error(f"Введенный путь {path} недоступен для чтения")
                raise PermissionError(f"Введенный путь {path} недоступен для чтения")
            try:
                remove(path)
                self._logger.info(f"Удалено {path}")
            except OSError:
                self._logger.exception(f"Ошибка удаления {path}")
                raise OSError(f"Ошибка удаления {path}")


    def zip(self, folder: PathLike[str] | str, filename: PathLike[str] | str) -> None:
        folder = Path(folder)
        filename = Path(filename)
        if not folder.exists():
            self._logger.error(f"Папка не найдена: {folder}")
            raise FileNotFoundError(folder)
        if not folder.is_dir():
            self._logger.error(f"Папка не является директорией: {folder}")
            raise NotADirectoryError(f"Папка не является директорией: {folder}")
        if not access(folder, R_OK):
            self._logger.error(f"Введенная папка {folder} недоступна для чтения")
            raise PermissionError(f"Введенная папка {folder} недоступна для чтения")
        try:
            with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as myzip:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = Path(root, file)
                        myzip.write(file_path, file_path.relative_to(folder))
            self._logger.info(f"Создан ZIP архив {filename.name} в {filename.parent}")
        except OSError:
            self._logger.exception(f"Ошибка создания ZIP архива {filename} из {folder}")
            raise OSError(f"Ошибка создания ZIP архива {filename} из {folder}")

    def unzip(self, filename: PathLike[str] | str) -> None:
        filename = Path(filename)
        if not filename.exists():
            self._logger.error(f"Файл не найден: {filename}")
            raise FileNotFoundError(filename)
        if not zipfile.is_zipfile(filename):
            self._logger.error(f"Файл не является ZIP архивом: {filename}")
            raise NotAZipFileError(f"Файл {filename} не является ZIP архивом")
        if not access(filename, R_OK):
            self._logger.error(f"Введенный файл {filename} недоступен для чтения")
            raise PermissionError(f"Введенный файл {filename} недоступен для чтения")
        try:
            with zipfile.ZipFile(filename, "r") as myzip:
                myzip.extractall()
                self._logger.info(f"Распакован {filename.name} в {Path.cwd()}")
        except (OSError, NotAZipFileError):
            self._logger.exception(f"Ошибка распаковки {filename}")
            raise OSError(f"Ошибка распаковки {filename}")


    def tar(self,
            folder: PathLike[str] | str,
            filename: PathLike[str] | str) -> None:
        folder = Path(folder)
        filename = Path(filename)
        if not folder.exists():
            self._logger.error(f"Папка не найдена: {folder}")
            raise FileNotFoundError(folder)
        if not folder.is_dir():
            self._logger.error(f"Папка не является директорией: {folder}")
            raise NotADirectoryError(f"Папка не является директорией: {folder}")
        if not access(folder, R_OK):
            self._logger.error(f"Введенная папка {folder} недоступна для чтения")
            raise PermissionError(f"Введенная папка {folder} недоступна для чтения")
        try:
            with tarfile.open(filename, "w:gz") as tar:
                tar.add(folder, arcname=folder.name)
            self._logger.info(f"Создан TAR.GZ архив {filename.name} из {folder}")
        except OSError:
            self._logger.exception(f"Ошибка создания TAR.GZ архива {filename}")
            raise OSError(f"Ошибка создания TAR.GZ архива {filename}")


    def untar(self,
              filename: PathLike[str] | str) -> None:
        filename = Path(filename)
        if not filename.exists():
            self._logger.error(f"Файл не найден: {filename}")
            raise FileNotFoundError(filename)
        if not access(filename, R_OK):
            self._logger.error(f"Введенный файл {filename} недоступен для чтения")
            raise PermissionError(f"Введенный файл {filename} недоступен для чтения")

        try:
            with tarfile.open(filename, "r:gz") as tar:
                tar.extractall()
                self._logger.info(f"Распакован {filename} в {Path.cwd()}")
        except OSError:
            self._logger.exception(f"Ошибка распаковки {filename}")
            raise OSError(f"Ошибка распаковки {filename}")


    def grep(
            self,
            pattern: str,
            path: PathLike[str] | str,
            recursive: bool,
            ignore_case: bool
    ) -> list[list[str]]:

        def all_files_on_directory(path_now=Path()) -> list[Path]:
            all_path = []
            for now_file in path_now.iterdir():
                if now_file.is_file():
                    all_path.append(now_file)
                elif now_file.is_dir():
                    all_path.extend(all_files_on_directory(now_file))
            return all_path

        try:
            if ignore_case:
                compiled_pattern = re.compile(pattern, flags=re.IGNORECASE | re.UNICODE)
            else:
                compiled_pattern = re.compile(pattern, flags=re.UNICODE)
        except re.error:
            self._logger.error(f"Ошибка компиляции регулярного выражения {pattern}")
            raise OSError(f"Ошибка компиляции регулярного выражения {pattern}")
        path = Path(path)
        result: list[list[str]] = []
        if not path.exists():
            self._logger.error(f"Путь не найден: {path}")
            raise FileNotFoundError(path)
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    for number, line in enumerate(file, start=1):
                        for match in compiled_pattern.finditer(line):
                            find_line = line[match.start():match.end()]
                            if find_line:
                                result.append([str(file.name), str(number), find_line])
            except OSError:
                self._logger.error(f"Ошибка открытия {path}")
                raise OSError(f"Ошибка открытия {path}")
        else:
            if recursive:
                all_path = all_files_on_directory(path)
            else:
                all_path = []
                for now_file in path.iterdir():
                    if now_file.is_file():
                        all_path.append(now_file)
            for now_file in all_path:
                try:
                    with open(now_file, "r", encoding="utf-8", errors="ignore") as file:
                        for number, line in enumerate(file, start=1):
                            for match in compiled_pattern.finditer(line):
                                find_line = line[match.start():match.end()]
                                if find_line:
                                    result.append([str(now_file), str(number), find_line])
                except OSError:
                    self._logger.error(f"Ошибка открытия {now_file}")
                    raise OSError(f"Ошибка открытия {now_file}")
        return result

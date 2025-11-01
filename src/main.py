import typer
from rich.table import Table
from rich.console import Console
from typer import Typer, Argument, Option
from logging import getLogger, config
from typing_extensions import Annotated
from src.common.config import LOGGING_CONFIG
from pathlib import Path
from src.services. luckyos_console import LuckyOSConsoleService
from src.common.config import check_and_clear_log_file


app = Typer()
console = Console()

config.dictConfig(LOGGING_CONFIG)
logger = getLogger(__name__)
service = LuckyOSConsoleService(logger=logger)

check_and_clear_log_file()

@app.command()
def ls(
        path: Annotated[Path, Argument(exists=False, readable=False, help="Путь к выводимой директории")] = Path.cwd(),
        long: Annotated[bool, Option("--long", "-l", help="Расширенный формат вывода")] = False
) -> None:
    """
    Выводит содержимое директории
    :param path: путь к выводимой директории
    :param long: флаг для расширенного формата вывода
    :return: таблицу с содержанием директории
    """
    try:
        content = service.ls(path, long)
        table = Table()
        if content and isinstance(content[0], str):
            table.add_column("Название файла", justify="left", style="cyan")
            for row  in content:
                if isinstance(row, str):
                    table.add_row(row.strip())
        else:
            table.add_column("Права", justify="center")
            table.add_column("Количество ссылок", justify="center")
            table.add_column("Размер (байт)", justify="center")
            table.add_column("Дата изменения", justify="center")
            table.add_column("Название файла", justify="center")
            for row in content:
                table.add_row(*map(str, row))
        console.print(table)
    except OSError as e:
        typer.echo(f"Ошибка: {e}")


@app.command()
def cd(
        path: Annotated[Path, Argument(exists=False, readable=False, help="Путь, в который нужно перейти")]
) -> None:
    """
        Изменяет текущую рабочую директорию
        :param path: путь к директории (поддерживает '..' для родительской и '~' для домашней)
        :return: выводит текущую директорию
    """
    try:
        service.cd(path)
        console.print(f"Текущая директория: {Path.cwd()}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")

@app.command()
def cat(
        filename: Annotated[Path, Argument(exists=False, readable=False, help="Название файла, которое нужно прочитать")]
) -> None:
    """
    Выводит содержимое файла
    :param filename: путь к файлу для чтения
    :return: содержимое файла
    """
    try:
        data = service.cat(filename)
        console.print(data)
    except OSError as e:
        typer.echo(f"Ошибка: {e}")


@app.command()
def cp(
        filename: Annotated[Path, Argument(exists=False, readable=False, help="Название копируемого файла")],
        path: Annotated[Path, Argument(exists=False, readable=False, help="Путь, куда нужно выполнить копирование")],
        recursive: Annotated[bool, Option("--recursive", "-r", help="Активация рекурсии")] = False
) -> None:
    """
    Копирует файл или директорию в указанное место
    :param filename: путь к файлу или директории для копирования
    :param path: путь назначения для копирования
    :param recursive: флаг для рекурсивного копирования директорий
    :return: сообщение об успешном копировании
    """
    try:
        service.cp(filename, path, recursive)
        console.print(f"Скопировано: {filename} -> {path}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")


@app.command()
def mv(
        path1: Annotated[Path, Argument(exists=False, readable=False, help="Файл или директория для перемещения/переименования")],
        path2: Annotated[Path, Argument(exists=False, readable=False, help="Директория куда нужно переместить искомые данные или переименованный исходный файл/директория")]
) -> None:
    """
    Перемещает или переименовывает файл/директорию
    :param path1: исходный путь к файлу или директории
    :param path2: путь назначения (может быть директорией или новым именем)
    :return: сообщение об успешном перемещении
    """
    try:
        service.mv(path1, path2)
        console.print(f"Перемещено: {path1} -> {path2}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")

@app.command()
def rm(
        paths: Annotated[list[Path], Argument(exists=False, readable=False, help="Файл или директория для удаления")],
        recursive: Annotated[bool, Option("--recursive", "-r", help="Активация рекурсивного удаления директории")] = False
) -> None:
    """
    Удаляет файл или директорию
    :param paths: список путей к файлам или директориям для удаления (один и более значений)
    :param recursive: флаг для рекурсивного удаления директорий (с подтверждением)
    :return: сообщение об успешном удалении
    """
    try:
        for path in paths:
            service.rm(path, recursive)
            console.print(f"Удалено: {path}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")

@app.command()
def zip(
        folder: Annotated[Path, Argument(exists=False, readable=False, help="Директорий, который нужно архивировать в zip")],
        filename: Annotated[Path, Argument(exists=False, readable=False, help="Путь, в который нужно сохранить архив (ввод с названием архива)")]
) -> None:
    """
    Создает ZIP архив из указанной директории
    :param folder: путь к директории для архивирования
    :param filename: путь к создаваемому ZIP архиву
    :return: сообщение об успешном создании архива
    """
    try:
        service.zip(folder, filename)
        console.print(f"Создан ZIP архив: {folder} -> {filename}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")


@app.command()
def unzip(
        filename: Annotated[Path, Argument(exists=False, readable=False, help="Путь к zip файлу, который нужно распаковать")]
) -> None:
    """
    Распаковывает ZIP архив в текущую директорию
    :param filename: путь к ZIP архиву для распаковки
    :return: сообщение об успешной распаковке
    """
    try:
        service.unzip(filename)
        console.print(f"Распакован ZIP архив: {filename} -> {Path.cwd()}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")


@app.command()
def tar(
        folder: Annotated[Path, Argument(exists=False, readable=False, help="Путь к директории, которую нужно архивировать")],
        filename: Annotated[Path, Argument(exists=False, readable=False, help="Путь сохранения архивированной директории")]
) -> None:
    """
    Создает TAR.GZ архив из указанной директории
    :param folder: путь к директории для архивирования
    :param filename: путь к создаваемому TAR.GZ архиву
    :return: сообщение об успешном создании архива
    """
    try:
        service.tar(folder, filename)
        console.print(f"Создан TAR.GZ архив: {folder} -> {filename}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")


@app.command()
def untar(
        filename: Annotated[Path, Argument(exists=False, readable=False, help="Путь к tar файлу для распаковки")]
) -> None:
    """
    Распаковывает TAR.GZ архив в текущую директорию
    :param filename: путь к TAR.GZ архиву для распаковки
    :return: сообщение об успешной распаковке
    """
    try:
        service.untar(filename)
        console.print(f"Распакован TAR.GZ архив: {filename} -> {Path.cwd()}")
    except OSError as e:
        typer.echo(f"Ошибка: {e}")

@app.command()
def grep(
        pattern: Annotated[str, Argument(help="Регулярное выражение")],
        path: Annotated[Path, Argument(exists=False, readable=False, help="Место поиска")],
        recursive: Annotated[bool, Option("-r", help="Рекурсивный поиск")] = False,
        ignore_case: Annotated[bool, Option("-i", "--ignore-case", help="Игнорирование регистра")] = False
) -> None:
    """
    Ищет совпадения регулярного выражения в файлах
    :param pattern: регулярное выражение для поиска
    :param path: путь к файлу или директории для поиска
    :param recursive: флаг для рекурсивного поиска в директориях
    :param ignore_case: флаг для игнорирования регистра при поиске
    :return: таблицу с результатами поиска (файл, строка, совпадение)
    """
    try:
        result: list[list[str]] = service.grep(pattern, path, recursive, ignore_case)
        if not result:
            console.print(f"Совпадения не найдены для паттерна '{pattern}' в {path}")
        table = Table()
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right", style="green")
        table.add_column("Match", style="yellow")

        for row in result:
            file_path, line_num, match = row
            table.add_row(str(file_path), str(line_num), match)
        console.print(table)
    except OSError as e:
        typer.echo(f"Ошибка: {e}")

if __name__ == "__main__":
    app()

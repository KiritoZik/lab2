from abc import ABC, abstractmethod
from os import PathLike
from typing import Union

class OSConsoleServiceBase(ABC):
    @abstractmethod
    def ls(self, path: PathLike[str] | str, long: bool) -> Union[list[str], list[list[object]]]:
        ...

    @abstractmethod
    def cd(self, path: PathLike[str] | str) -> None:
        ...

    @abstractmethod
    def cat(self, filename: PathLike[str] | str) -> str:
        ...


    @abstractmethod
    def cp(
            self,
            filename: PathLike[str] | str,
            path: PathLike[str] | str,
            recursive: bool
    ) -> None:
        ...

    @abstractmethod
    def mv(
            self,
            path1: PathLike[str] | str,
            path2: PathLike[str] | str,) -> None:
        ...

    @abstractmethod
    def rm(self,
           path: PathLike[str] | str,
           recursive: bool):
        ...

    @abstractmethod

    def zip(self,
            folder: PathLike[str] | str,
            filename: PathLike[str] | str) -> None:
        ...

    @abstractmethod
    def unzip(self ,
              filename: PathLike[str] | str) -> None:
        ...

    @abstractmethod
    def tar(self,
            folder: PathLike[str] | str,
            filename: PathLike[str] | str) -> None:
        ...

    @abstractmethod
    def untar(self,
              filename: PathLike[str] | str) -> None:
        ...

    @abstractmethod
    def grep(
            self,
            pattern: str,
            path: PathLike[str] | str,
            recursive: bool,
            ignore_case: bool
    ) -> list[list[str]]:
        ...

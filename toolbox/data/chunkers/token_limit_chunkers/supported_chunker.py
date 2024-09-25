import os.path

from toolbox.constants.code_extensions import CODE_EXTENSIONS
from toolbox.constants.symbol_constants import EMPTY_STRING
from toolbox.data.chunkers.token_limit_chunkers.dummy_code_chunker import DummyCodeChunker
from toolbox.data.chunkers.token_limit_chunkers.java_chunker import JavaChunker
from toolbox.data.chunkers.token_limit_chunkers.natural_language_chunker import NaturalLanguageChunker
from toolbox.data.chunkers.token_limit_chunkers.python_chunker import PythonChunker
from toolbox.util.file_util import FileUtil
from toolbox.util.supported_enum import SupportedEnum


class SupportedChunker(SupportedEnum):
    PY = PythonChunker
    JAVA = JavaChunker
    NL = NaturalLanguageChunker
    CODE = DummyCodeChunker

    @staticmethod
    def determine_from_path(path_to_file: str = None) -> "SupportedChunker":
        """
        Gets the chunker responsible for breaking a file or content into smaller pieces for the model
        :param path_to_file: The path to the file being chunked
        :return: The chunker to use
        """
        default = SupportedChunker.NL
        if not path_to_file:
            return default
        ext = FileUtil.get_file_ext(path_to_file).split(".")[-1]
        chunker_type = SupportedChunker.get_chunker_from_ext(ext)
        return chunker_type

    @staticmethod
    def get_chunker_from_ext(ext: str) -> "SupportedChunker":
        """
        Gets the chunker responsible for breaking content into smaller pieces for the model
        :param ext: The ext of the file being chunked
        :return: The chunker to use
        """
        if not isinstance(ext, str):
            ext = str(ext)
        tmp = os.path.splitext(ext)
        if tmp[-1]:
            ext = tmp[-1].replace(os.extsep, EMPTY_STRING)
        ext = ext.upper()
        try:
            return SupportedChunker[ext]
        except KeyError:
            if ext in CODE_EXTENSIONS:
                return SupportedChunker.CODE
            return SupportedChunker.NL

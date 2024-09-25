from enum import Enum

from toolbox.data.processing.cleaning.extract_code_identifiers import ExtractCodeIdentifiersStep
from toolbox.data.processing.cleaning.filter_min_length_step import FilterMinLengthStep
from toolbox.data.processing.cleaning.lemmatize_words_step import LemmatizeWordStep
from toolbox.data.processing.cleaning.manual_replace_words_step import ManualReplaceWordsStep
from toolbox.data.processing.cleaning.regex_replacement_step import RegexReplacementStep
from toolbox.data.processing.cleaning.remove_non_alpha_chars_step import RemoveNonAlphaCharsStep
from toolbox.data.processing.cleaning.remove_unwanted_chars_step import RemoveUnwantedCharsStep
from toolbox.data.processing.cleaning.remove_white_space_step import RemoveWhiteSpaceStep
from toolbox.data.processing.cleaning.separate_camel_case_step import SeparateCamelCaseStep
from toolbox.data.processing.cleaning.separate_joined_words_step import SeparateJoinedWordsStep
from toolbox.data.processing.cleaning.shuffle_words_step import ShuffleWordsStep


class SupportedDataCleaningStep(Enum):
    """
    Enumerated list of supported data cleaning steps.
    """
    FILTER_MIN_LENGTH = FilterMinLengthStep
    SHUFFLE_WORDS = ShuffleWordsStep
    REMOVE_UNWANTED_CHARS = RemoveUnwantedCharsStep
    SEPARATE_JOINED_WORDS = SeparateJoinedWordsStep
    REPLACE_WORDS = ManualReplaceWordsStep
    REMOVE_WHITE_SPACE = RemoveWhiteSpaceStep
    REMOVE_NON_ALPHA = RemoveNonAlphaCharsStep
    SEPARATE_CAMEL_CASE = SeparateCamelCaseStep
    LEMMATIZE_WORDS = LemmatizeWordStep
    REGEX_REPLACEMENTS = RegexReplacementStep
    EXTRACT_CODE_IDENTIFIERS = ExtractCodeIdentifiersStep

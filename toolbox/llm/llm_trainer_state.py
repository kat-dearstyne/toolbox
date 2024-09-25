from dataclasses import dataclass
from typing import List, Union

from toolbox.data.managers.trainer_dataset_manager import TrainerDatasetManager
from toolbox.llm.abstract_llm_manager import AbstractLLMManager
from toolbox.llm.llm_task import LLMCompletionType
from toolbox.llm.prompts.prompt_builder import PromptBuilder
from toolbox.pipeline.state import State
from toolbox.util.dataclass_util import required_field


@dataclass
class LLMTrainerState(State):
    """
    Represents a state of the LLMTrainer in time
    """
    """
    :param prompt_builder: Creates the prompts for trace link prediction.
    """
    prompt_builders: Union[PromptBuilder, List[PromptBuilder]] = required_field(field_name="prompt_builder")
    """
    :param trainer_dataset_manager: The dataset manager for training and prediction
    """
    trainer_dataset_manager: TrainerDatasetManager = None
    """
    :param llm_manager: The manager incharge of the lLM being used
    """
    llm_manager: AbstractLLMManager = required_field(field_name="llm_manager")
    """
    :param completion_type: The type of completion (either generation or completion)
    """
    completion_type: LLMCompletionType = LLMCompletionType.GENERATION

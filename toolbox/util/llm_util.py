from typing import Callable, Dict, Iterable, List, Tuple, TypeVar

from toolbox.data.keys.prompt_keys import PromptKeys
from toolbox.data.objects.artifact import Artifact
from toolbox.infra.t_logging.logger_manager import logger
from toolbox.llm.abstract_llm_manager import AbstractLLMManager
from toolbox.llm.llm_trainer import LLMTrainer
from toolbox.llm.prompts.prompt_builder import PromptBuilder
from toolbox.util.enum_util import EnumDict

PromptGeneratorReturnType = Tuple[PromptBuilder, EnumDict]
PromptGeneratorType = Callable[[Artifact], PromptGeneratorReturnType]

ItemType = TypeVar("ItemType")


class LLMUtil:
    @staticmethod
    def complete_iterable_prompts(items: Iterable[ItemType],
                                  prompt_generator: Callable[[Artifact], Tuple[PromptBuilder, EnumDict]],
                                  llm_manager: AbstractLLMManager) -> List[Tuple[ItemType, Dict]]:
        """
        Builds and completes prompts for some iterable.
        :param items: The items to iterate over and create prompts for.
        :param prompt_generator: Callable function that creates prompt per item.
        :param llm_manager: The LLM manager used to complete the prompts.
        """
        prompts: List[EnumDict] = []
        builders: List[PromptBuilder] = []
        for a in items:
            a_builder, a_prompt = prompt_generator(a)
            builders.append(a_builder)
            prompts.append(a_prompt)

        message_prompts = [p[PromptKeys.PROMPT] for p in prompts]
        system_prompts = [p[PromptKeys.SYSTEM] if p.get(PromptKeys.SYSTEM, None) else None for p in prompts]
        output = LLMTrainer.predict_from_prompts(llm_manager=llm_manager,
                                                 prompt_builders=builders,
                                                 message_prompts=message_prompts,
                                                 system_prompts=system_prompts)

        parsed_responses = []
        for artifact, builder, prediction in zip(items, builders, output.predictions):
            if prediction is None:
                logger.info(f"Unable to parse response for artifact: {artifact}")
                continue
            prompt_id = builder.prompts[-1].args.prompt_id
            parsed_artifact_response = prediction[prompt_id]
            parsed_responses.append(parsed_artifact_response)
        return list(zip(items, parsed_responses))

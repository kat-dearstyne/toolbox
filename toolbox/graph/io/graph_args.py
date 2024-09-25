from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from toolbox.constants.symbol_constants import EMPTY_STRING
from toolbox.data.exporters.serializable_exporter import SerializableExporter
from toolbox.data.tdatasets.prompt_dataset import PromptDataset
from toolbox.graph.io.graph_state import GraphState
from toolbox.pipeline.args import Args
from toolbox.util.pythonisms_util import default_mutable_type
from toolbox.util.reflection_util import ReflectionUtil
from toolbox.util.unknown_params_lambda import UnknownParamsLambda

converters = {PromptDataset: UnknownParamsLambda(lambda val: SerializableExporter(dataset=val).export()),
              "artifacts_referenced_in_question": UnknownParamsLambda(lambda val, dataset: dataset.artifact_df.to_artifacts(set(val)))}


@dataclass
class GraphArgs(Args):
    user_question: str = EMPTY_STRING
    chat_history: List[Tuple[str, str]] = None
    artifacts_referenced_in_question: List[str] | str = None
    context_filepath: Optional[str] = None
    artifact_types: List[str] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """
        Runs post-initialization steps to set appropriate variables.
        :return: None.
        """
        super().__post_init__()
        self.artifact_types = self.dataset.artifact_df.get_artifact_types()
        if isinstance(self.artifacts_referenced_in_question, str):
            self.artifacts_referenced_in_question = [self.artifacts_referenced_in_question]

    def to_graph_input(self, state_class: GraphState = GraphState, **overriding_args) -> Dict:
        """
        Creates the input dictionary for the langgraph.
        :param state_class: The input/state class used for graph.
        :param overriding_args: Any vars to override the state with.
        :return: The input dictionary for the langgraph.
        """
        params = {}
        for var_name, var_type in state_class.__annotations__.items():
            val = overriding_args[var_name] if var_name in overriding_args else getattr(self, var_name, None)
            if val:
                converter_key = var_name if var_name in converters else type(val)
                if converter_key in converters:
                    val = converters[converter_key](val=val, **vars(self))

                assert ReflectionUtil.is_type(val, var_type, var_name), f"{var_name} is not of expected type {var_type}. " \
                                                                        f"Got {type(var_name)} instead."
                params[var_name] = val
            else:
                params[var_name] = default_mutable_type(var_type)
        inputs = state_class(**params)
        return inputs

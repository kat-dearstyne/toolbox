from abc import ABC, abstractmethod
from typing import Any, Dict, List

from toolbox.graph.branches.paths.path_choices import PathChoices
from toolbox.graph.branches.paths.path_selector import PathSelector
from toolbox.graph.nodes.abstract_node import AbstractNode
from toolbox.graph.nodes.supported_nodes import SupportedNodes


class BaseBranch(AbstractNode, ABC):
    BASE_NAME = "Branch"

    def perform_action(self, state: Dict, run_async: bool = False) -> Any:
        """
        Chooses what node to go to next based on the current state.
        :param state: The current state of the graph.
        :param run_async: If true, runs in async mode, otherwise runs sync.
        :return: The name of the next node to visit.
        """
        return self.choose_path(state)

    def choose_path(self, state: Dict, default: SupportedNodes = None) -> str:
        """
        Chooses what node to go to next based on the state.
        :param state: The current state.
        :param default: The default selection if no condition is met.
        :return: The name of the next node to visit.
        """
        paths = self.path_choices.get_all_paths(default)
        branch = PathSelector(*paths)
        return branch.select(state)

    def get_node_choices(self) -> List[SupportedNodes]:
        """
        Gets all possible next node choices.
        :return: All possible next node choices.
        """
        node_choices = [path.action for path in self.path_choices.get_all_paths()]
        return node_choices

    @property
    @abstractmethod
    def path_choices(self) -> PathChoices:
        """
        Contains all possible paths that can be taken based on the state.
        :return:  All possible paths that can be taken based on the state.
        """

from typing import Dict

from toolbox.pipeline.abstract_pipeline import AbstractPipeline
from toolbox.summarize.summarizer_args import SummarizerArgs
from toolbox.traceability.ranking.common.ranking_args import RankingArgs
from toolbox.traceability.ranking.common.ranking_state import RankingState
from toolbox.traceability.ranking.steps.select_candidate_links_step import SelectCandidateLinksStep
from toolbox.traceability.ranking.steps.sort_children_step import SortChildrenStep
from toolbox.util.ranking_util import RankingUtil


class SearchPipeline(AbstractPipeline[RankingArgs, RankingState]):
    """
    Sorts a set of artifacts from most to least similar to some target artifacts.
    """
    steps = [SortChildrenStep, SelectCandidateLinksStep]

    def __init__(self, args: RankingArgs):
        """
        Ranks children artifacts from most to least related to source.
        :param args: Arguments to the ranking pipeline.
        """
        summarizer_args = SummarizerArgs(
            project_summary_sections=[],
            do_resummarize_artifacts=False
        )
        super().__init__(args, SearchPipeline.steps, summarizer_args=summarizer_args)

    def state_class(self) -> RankingState:
        """
        Creates new ranking state.
        :return: The new state.
        """
        return RankingState

    def run(self) -> None:
        """
        :return: List of parents mapped to their ranked children.
        """
        super().run()

    def get_input_output_counts(self) -> Dict[str, int]:
        """
        Gets the number of selected traces for the pipeline
        :return:  Gets the number of selected traces for the pipeline
        """
        return RankingUtil.get_input_output_counts(self.state)

from typing import List

from toolbox.data.objects.trace import Trace
from toolbox.traceability.ranking.trace_selectors.i_selection_method import iSelector
from toolbox.traceability.ranking.trace_selectors.select_by_threshold import SelectByThreshold
from toolbox.util.ranking_util import RankingUtil


class SelectByThresholdScaledAcrossAll(iSelector):

    @staticmethod
    def select(candidate_entries: List[Trace], threshold: float, **kwargs) -> List[Trace]:
        """
        Filters the candidate links based on score threshold after score are normalized based on min and max for parent
        :param candidate_entries: Candidate trace entries
        :param threshold: The threshold to filter by
        :return: filtered list of entries
        """
        RankingUtil.normalized_scores_based_on_parent(candidate_entries)
        return SelectByThreshold.select(candidate_entries, threshold)

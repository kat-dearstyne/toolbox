from unittest import TestCase

from toolbox.data.dataframes.artifact_dataframe import ArtifactDataFrame
from toolbox.data.keys.structure_keys import TraceKeys
from toolbox.data.tdatasets.prompt_dataset import PromptDataset
from toolbox.traceability.ranking.common.ranking_args import RankingArgs
from toolbox.traceability.ranking.common.ranking_state import RankingState
from toolbox.traceability.ranking.steps.select_candidate_links_step import SelectCandidateLinksStep
from toolbox.traceability.ranking.trace_selectors.selection_by_threshold_scaled_by_artifact import \
    SelectByThresholdScaledByArtifacts
from toolbox.traceability.ranking.trace_selectors.selection_methods import SupportedSelectionMethod
from toolbox.util.enum_util import EnumDict
from toolbox.util.ranking_util import RankingUtil
from toolbox_test.traceability.ranking.steps.ranking_pipeline_test import DEFAULT_CHILDREN_IDS, DEFAULT_PARENT_IDS


class TestSelectCandidateLinksStep(TestCase):

    def test_run(self):
        parent_ids = DEFAULT_PARENT_IDS
        children_ids = DEFAULT_CHILDREN_IDS
        args = RankingArgs(parent_ids=parent_ids, children_ids=children_ids, dataset=PromptDataset(artifact_df=ArtifactDataFrame()),
                           types_to_trace=("target", "source"))

        expected_links_by_threshold = [2, 4]
        state = self.get_state(children_ids, parent_ids)
        args.selection_method = SupportedSelectionMethod.SELECT_BY_THRESHOLD
        SelectCandidateLinksStep().run(args, state)
        self.assertEqual(len(state.selected_entries), len(expected_links_by_threshold))
        self.assert_links(expected_links_by_threshold, state)

        expected_links_by_parent = [2, 3, 4]
        state = self.get_state(children_ids, parent_ids)
        args.selection_method = SupportedSelectionMethod.SELECT_TOP_PARENTS
        SelectCandidateLinksStep().run(args, state)
        self.assert_links(expected_links_by_parent, state)

        expected_links_by_normalized_children = [2, 4]
        state = self.get_state(children_ids, parent_ids)
        args.selection_method = SupportedSelectionMethod.SELECT_BY_THRESHOLD_SCALED
        selection_method: SelectByThresholdScaledByArtifacts = args.selection_method.value
        state.selected_entries = selection_method.select(state.get_current_entries(),
                                                         threshold=args.link_threshold,
                                                         parent_thresholds=args.parent_thresholds,
                                                         artifact_type=
                                                         TraceKeys.parent_label(),
                                                         )
        self.assert_links(expected_links_by_normalized_children, state)

        expected_links_by_normalized_parent = [2, 3, 4]
        state = self.get_state(children_ids, parent_ids)
        args.selection_method = SupportedSelectionMethod.SELECT_BY_THRESHOLD_SCALED
        selection_method: SelectByThresholdScaledByArtifacts = args.selection_method.value
        state.selected_entries = selection_method.select(state.get_current_entries(),
                                                         threshold=args.link_threshold,
                                                         parent_thresholds=args.parent_thresholds,
                                                         artifact_type=
                                                         TraceKeys.child_label()
                                                         )
        self.assert_links(expected_links_by_normalized_parent, state)

        expected_links_none = [1, 2, 3, 4]
        state = self.get_state(children_ids, parent_ids)
        args.selection_method = None
        SelectCandidateLinksStep().run(args, state)
        self.assert_links(expected_links_none, state)

        expected_links_missing = [1, 2, 3, 4]
        state = self.get_state(children_ids, parent_ids)
        for entry in state.candidate_entries:
            entry["score"] = 0
        args.selection_method = SupportedSelectionMethod.SELECT_BY_THRESHOLD
        SelectCandidateLinksStep().run(args, state)
        self.assert_links(expected_links_missing, state)

    def assert_links(self, expected_links, state):
        selected_link_ids = set([link[TraceKeys.LINK_ID] for link in state.selected_entries])
        expected_link_ids = set(expected_links)
        self.assertEqual(expected_link_ids, selected_link_ids)

    @staticmethod
    def get_state(children_ids, parent_ids):
        children_entries = [EnumDict({'link_id': 1, 'source': 't6', 'target': 's4', 'score': 0.4}),
                            EnumDict({'link_id': 2, 'source': 't1', 'target': 's4', 'score': 0.7}),
                            EnumDict({'link_id': 3, 'source': 't6', 'target': 's5', 'score': 0.5}),
                            EnumDict({'link_id': 4, 'source': 't1', 'target': 's5', 'score': 0.7})
                            ]
        return RankingState(sorted_parent2children={p_id: [RankingUtil.create_entry(p_id, c_id) for c_id in children_ids]
                                                    for p_id in parent_ids}, candidate_entries=children_entries)

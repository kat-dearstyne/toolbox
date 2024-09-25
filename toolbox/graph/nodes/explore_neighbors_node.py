from typing import Dict, List, Set

from langchain_core.documents.base import Document

from toolbox.data.keys.structure_keys import ArtifactKeys
from toolbox.data.objects.artifact import Artifact
from toolbox.data.tdatasets.prompt_dataset import PromptDataset
from toolbox.graph.io.graph_state import GraphState
from toolbox.graph.nodes.abstract_node import AbstractNode
from toolbox.util.dict_util import DictUtil


class ExploreNeighborsNode(AbstractNode):

    def perform_action(self, state: GraphState, run_async: bool = False):
        """
        Retrieve neighboring artifacts .
        :param run_async: If True, runs in async mode else synchronously.
        :param state: The current state of the graph.
        """
        dataset = self.graph_args.dataset
        next_search = {a_id: a_id for a_id in state["selected_artifact_ids"]
                       if a_id in dataset.artifact_df and a_id not in state["documents"]}

        related_artifacts = self._get_selected_traces(dataset, next_search)

        state["documents"].update(related_artifacts)
        return state

    @staticmethod
    def _get_selected_traces(dataset: PromptDataset,
                             query_artifact_ids: Dict[str, Set[str]]) -> Dict[str, List[Document]]:
        """
        Finds all traces related to the given artifact ids.
        :param dataset: Contains all artifacts and traces.
        :param query_artifact_ids: A dictionary mapping  a id to query to the original query id that it originated from.
        :return: A dictionary mapping query artifact id to a list of selected related artifacts
        """
        selected_relationships = {}
        current_queries = list(query_artifact_ids.keys())
        traces = dataset.trace_dataset.trace_df.get_relationships(current_queries)

        for trace in traces:
            artifacts = dataset.artifact_df.get_artifacts_from_trace(trace)
            query_artifact_index = [i for i, a in enumerate(artifacts) if a[ArtifactKeys.ID] in query_artifact_ids][0]

            query_artifact, other_artifact = artifacts[query_artifact_index], artifacts[1 - query_artifact_index]
            original_query_id = query_artifact_ids[query_artifact[ArtifactKeys.ID]]
            DictUtil.set_or_append_item(selected_relationships, original_query_id,
                                        Artifact.convert_to_document(other_artifact))

        return selected_relationships

from typing import Dict, List

from toolbox.data.dataframes.artifact_dataframe import ArtifactDataFrame
from toolbox.data.dataframes.layer_dataframe import LayerDataFrame
from toolbox.data.dataframes.trace_dataframe import TraceDataFrame
from toolbox.data.keys.structure_keys import ArtifactKeys, LayerKeys, StructuredKeys, TraceKeys
from toolbox.data.managers.trainer_dataset_manager import TrainerDatasetManager
from toolbox.data.tdatasets.dataset_role import DatasetRole
from toolbox.data.tdatasets.trace_dataset import TraceDataset
from toolbox.traceability.output.trace_train_output import TraceTrainOutput
from toolbox.traceability.ranking.sorters.i_sorter import iSorter
from toolbox.traceability.vsm.vsm_job import VSMJob
from toolbox.util.status import Status


class VSMSorter(iSorter):

    @staticmethod
    def sort(parent_ids: List[str], child_ids: List[str], artifact_map: Dict[str, str],
             return_scores: bool = False, **kwargs) -> Dict[str, List]:
        """
        Sorts the children artifacts from most to least similar to the parent artifacts using VSM.
        :param parent_ids: The artifact ids of the parents.
        :param child_ids: The artifact ids of the children.
        :param artifact_map: Map of ID to artifact bodies.
        :param return_scores: Whether to return the similarity scores
        :return: Map of parent to list of sorted children.
        """

        parent_tag_name = TraceKeys.parent_label().value
        child_tag_name = TraceKeys.child_label().value
        artifact_names = parent_ids + child_ids
        artifact_content = [artifact_map[a_name] for a_name in artifact_names]
        artifact_df = ArtifactDataFrame({ArtifactKeys.ID: artifact_names,
                                         ArtifactKeys.CONTENT: artifact_content,
                                         ArtifactKeys.LAYER_ID: [parent_tag_name for source in parent_ids] +
                                                                [child_tag_name for target in child_ids]})
        layer_df = LayerDataFrame({LayerKeys.SOURCE_TYPE: [child_tag_name], LayerKeys.TARGET_TYPE: [parent_tag_name]})
        dataset = TraceDataset(artifact_df=artifact_df, trace_df=TraceDataFrame(), layer_df=layer_df)
        trainer_dataset_manager = TrainerDatasetManager.create_from_datasets({DatasetRole.EVAL: dataset, DatasetRole.TRAIN: dataset})
        vsm_job = VSMJob(trainer_dataset_manager=trainer_dataset_manager, select_predictions=False)
        job_result = vsm_job.run()
        assert job_result.status == Status.SUCCESS, f"Sorting using VSM failed. {job_result.body}"
        vsm_result: TraceTrainOutput = job_result.body
        prediction_entries = vsm_result.prediction_output.prediction_entries
        unsorted_targets = {}
        for entry in prediction_entries:
            source = entry[parent_tag_name]
            target = entry[child_tag_name]
            if source not in unsorted_targets:
                unsorted_targets[source] = {}
            unsorted_targets[source][target] = entry[StructuredKeys.SCORE]
        sorted_targets = {source: sorted(targets2score, key=targets2score.get, reverse=True) for source, targets2score in
                          unsorted_targets.items()}
        if return_scores:
            sorted_targets = {source: (sorted_children, [unsorted_targets[source][c] for c in sorted_children])
                              for source, sorted_children in sorted_targets.items()}
        return sorted_targets

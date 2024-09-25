from toolbox.data.creators.multi_trace_dataset_creator import MultiTraceDatasetCreator
from toolbox.data.creators.trace_dataset_creator import TraceDatasetCreator
from toolbox.infra.experiment.definition_creator import DefinitionCreator
from toolbox.infra.experiment.variables.typed_definition_variable import TypedDefinitionVariable
from toolbox_test.base.paths.project_paths import toolbox_TEST_PROJECT_CSV_PATH, toolbox_TEST_PROJECT_STRUCTURE_PATH
from toolbox_test.base.tests.base_test import BaseTest
from toolbox_test.testprojects.csv_test_project import CsvTestProject
from toolbox_test.testprojects.structured_test_project import StructuredTestProject


class TestMultiTraceDatasetCreator(BaseTest):

    def test_create(self):
        """
        Tests that creating multi-dataset contains the datasets within it.
        """
        multi_dataset_creator = self.get_multi_trace_dataset_creator()
        multi_dataset = multi_dataset_creator.create()
        expected_projects = [StructuredTestProject(), CsvTestProject()]
        expected_datasets = [TraceDatasetCreator(project.get_project_reader()).create() for project in expected_projects]
        for dataset in expected_datasets:
            for link_id in dataset.trace_df.index:
                self.assertIn(link_id, multi_dataset.trace_df)
            for link_id in dataset._pos_link_ids:
                self.assertIn(link_id, multi_dataset._pos_link_ids)
            for link_id in dataset._neg_link_ids:
                self.assertIn(link_id, multi_dataset._neg_link_ids)

    @staticmethod
    def get_multi_trace_dataset_creator():
        dataset_creator_definition_multi = {
            "project_readers": [{
                TypedDefinitionVariable.OBJECT_TYPE_KEY: "STRUCTURE",
                "project_path": toolbox_TEST_PROJECT_STRUCTURE_PATH
            }, {
                TypedDefinitionVariable.OBJECT_TYPE_KEY: "CSV",
                "project_path": toolbox_TEST_PROJECT_CSV_PATH,
                "overrides": {
                    "allowed_orphans": 2
                }
            }]
        }
        return DefinitionCreator.create(MultiTraceDatasetCreator, dataset_creator_definition_multi)

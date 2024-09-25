from typing import List

from toolbox.data.objects.artifact import Artifact
from toolbox.data.readers.dataframe_project_reader import DataFrameProjectReader
from toolbox_test.base.paths.project_paths import toolbox_TEST_PROJECT_DATAFRAME_PATH
from toolbox_test.testprojects.abstract_test_project import AbstractTestProject
from toolbox_test.testprojects.safa_test_project import SafaTestProject


class DataFrameTestProject(AbstractTestProject):
    """
    Contains safa test project testing details.
    """

    @classmethod
    def get_source_artifacts(cls) -> List[Artifact]:
        return SafaTestProject.get_source_artifacts()

    @classmethod
    def get_target_artifacts(cls) -> List[Artifact]:
        return SafaTestProject.get_target_artifacts()

    @staticmethod
    def get_n_links() -> int:
        return 12

    @classmethod
    def get_n_positive_links(cls) -> int:
        return 6

    @staticmethod
    def get_project_path() -> str:
        """
        :return: Returns path to safa project.
        """
        return toolbox_TEST_PROJECT_DATAFRAME_PATH

    @classmethod
    def get_project_reader(cls) -> DataFrameProjectReader:
        """
        :return: Returns structured project reader for project
        """
        return DataFrameProjectReader(project_path=DataFrameTestProject.get_project_path(),
                                      artifact_df_filename="artifact_df.csv",
                                      trace_df_filename="trace_df.csv",
                                      layer_df_filename="layer_df.csv",
                                      overrides={"allowed_orphans": 2, "remove_orphans": True})

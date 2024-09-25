from toolbox.data.keys.structure_keys import ArtifactKeys
from toolbox.data.readers.abstract_project_reader import AbstractProjectReader
from toolbox.data.readers.artifact_project_reader import ArtifactProjectReader
from toolbox.summarize.artifact.artifacts_summarizer import ArtifactsSummarizer
from toolbox_test.base.constants import SUMMARY_FORMAT
from toolbox_test.base.mock.decorators.anthropic import mock_anthropic
from toolbox_test.base.mock.test_ai_manager import TestAIManager
from toolbox_test.base.tests.base_test import BaseTest
from toolbox_test.testprojects.artifact_test_project import ArtifactTestProject
from toolbox_test.testprojects.dataframe_test_project import DataFrameTestProject


class TestArtifactProjectReader(BaseTest):
    """
    Tests that artifact project is correctly parsed.
    """
    test_project = ArtifactTestProject()

    @mock_anthropic
    def test_summarization(self, ai_manager: TestAIManager):
        """
        Tests that project artifacts can be summarized
        """
        ai_manager.mock_summarization()
        project_reader: AbstractProjectReader = self.test_project.get_project_reader()
        project_reader.set_summarizer(ArtifactsSummarizer(summarize_code_only=False))
        artifact_df = project_reader.read_project()
        summary_artifacts = self.test_project.get_artifact_entries()
        for row in summary_artifacts:
            row[ArtifactKeys.SUMMARY.value] = SUMMARY_FORMAT.format(row[ArtifactKeys.CONTENT.value])
        self.verify_entities_in_df(summary_artifacts, artifact_df)

    def test_read_project(self):
        """
        Tests that the artifact project can be read and translated to artifact data frame.
        """
        project_reader = self.test_project.get_project_reader()
        artifact_df = project_reader.read_project()
        self.verify_entities_in_df(self.test_project.get_artifact_entries(), artifact_df)

    def test_read_project_from_csv(self):
        """
        Tests that the artifact project can be read and translated to artifact data frame.
        """
        test_project = DataFrameTestProject
        project_path = test_project.get_project_path()
        project_reader = ArtifactProjectReader(project_path)
        artifact_df = project_reader.read_project()
        self.verify_entities_in_df(test_project.get_artifact_entries(), artifact_df)

import json
import os

from toolbox.data.keys.prompt_keys import PromptKeys
from toolbox.data.readers.prompt_project_reader import PromptProjectReader
from toolbox.summarize.artifact.artifacts_summarizer import ArtifactsSummarizer
from toolbox_test.base.constants import SUMMARY_FORMAT
from toolbox_test.base.mock.decorators.anthropic import mock_anthropic
from toolbox_test.base.mock.test_ai_manager import TestAIManager
from toolbox_test.base.paths.project_paths import toolbox_TEST_PROJECT_PROMPT_LHP_PATH
from toolbox_test.base.tests.base_test import BaseTest


class TestPromptProjectReader(BaseTest):
    """
    Tests that csv project is correctly parsed.
    """
    DATASET_PATH = toolbox_TEST_PROJECT_PROMPT_LHP_PATH

    @mock_anthropic
    def test_summarization(self, ai_manager: TestAIManager):
        """
        Tests that project artifacts can be summarized
        """
        ai_manager.mock_summarization()
        project_reader = self.get_project_reader()
        project_reader.set_summarizer(ArtifactsSummarizer(summarize_code_only=False))
        prompts_df = project_reader.read_project()
        expected_prompts = []
        with open(self.DATASET_PATH) as file:
            for line in file.readlines():
                prompt_dict = json.loads(line)
                prompt_dict[PromptKeys.PROMPT.value] = SUMMARY_FORMAT.format(prompt_dict[PromptKeys.PROMPT.value]) \
                    .replace(os.linesep, "")
                expected_prompts.append(prompt_dict)
        prompts_df[PromptKeys.PROMPT] = [row[PromptKeys.PROMPT].replace(os.linesep, "") for i, row in prompts_df.itertuples()]
        self.verify_entities_in_df(expected_prompts, prompts_df)

    def test_read_project(self):
        """
        Tests that the csv project can be read and translated to data frames.
        """
        project_reader = self.get_project_reader()
        prompts_df = project_reader.read_project()
        expected_prompts = []
        with open(self.DATASET_PATH) as file:
            for line in file.readlines():
                expected_prompts.append(json.loads(line))
        self.verify_entities_in_df(expected_prompts, prompts_df)

    def get_project_reader(self) -> PromptProjectReader:
        """
        Gets the prompt project reader for the project
        :return: The prompt project reader for the project
        """
        return PromptProjectReader(self.DATASET_PATH)

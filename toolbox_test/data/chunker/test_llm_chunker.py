from toolbox.constants.symbol_constants import NEW_LINE
from toolbox.data.chunkers.llm_chunker import LLMChunker
from toolbox.data.objects.artifact import Artifact
from toolbox.util.prompt_util import PromptUtil
from toolbox_test.base.mock.decorators.anthropic import mock_anthropic
from toolbox_test.base.mock.test_ai_manager import TestAIManager
from toolbox_test.base.tests.base_test import BaseTest
from toolbox_test.data.chunker.constants import CHUNK_TEST_SENTENCE
from toolbox_test.data.chunker.util import get_test_chunks, verify_test_chunks


class TestLLMChunker(BaseTest):

    @mock_anthropic
    def test_chunk(self, mock_ai: TestAIManager):
        """
        Chunks sentence and verifies that each chunk was accurately computed.
        """
        expected_chunks = get_test_chunks()
        mock_ai.set_responses([NEW_LINE.join([PromptUtil.create_xml("chunk", chunk) for chunk in expected_chunks])])
        artifact = Artifact(id=1, content=CHUNK_TEST_SENTENCE, layer_id="layer")
        chunks = LLMChunker().chunk([artifact])[0]
        verify_test_chunks(self, chunks, expected_chunks=expected_chunks)

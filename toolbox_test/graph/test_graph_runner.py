from unittest.mock import MagicMock

import httpx
from anthropic._exceptions import InternalServerError
from langgraph.constants import START

from toolbox.data.dataframes.artifact_dataframe import ArtifactDataFrame
from toolbox.data.dataframes.layer_dataframe import LayerDataFrame
from toolbox.data.dataframes.trace_dataframe import TraceDataFrame
from toolbox.data.keys.structure_keys import LayerKeys, TraceKeys
from toolbox.data.objects.artifact import Artifact
from toolbox.data.tdatasets.prompt_dataset import PromptDataset
from toolbox.data.tdatasets.trace_dataset import TraceDataset
from toolbox.graph.branches.paths.path import Path
from toolbox.graph.branches.paths.path_selector import PathSelector
from toolbox.graph.branches.supported_branches import SupportedBranches
from toolbox.graph.edge import Edge
from toolbox.graph.graph_definition import GraphDefinition
from toolbox.graph.graph_runner import GraphRunner
from toolbox.graph.io.graph_args import GraphArgs
from toolbox.graph.io.graph_state import GraphState
from toolbox.graph.io.graph_state_vars import GraphStateVars
from toolbox.graph.llm_tools.tool_models import ExploreArtifactNeighborhood, RequestAssistance, RetrieveAdditionalInformation, \
    AnswerUser
from toolbox.graph.nodes.generate_node import GenerateNode
from toolbox.graph.nodes.supported_nodes import SupportedNodes
from toolbox_test.base.mock.decorators.anthropic import mock_anthropic
from toolbox_test.base.mock.decorators.chat import mock_chat_model
from toolbox_test.base.mock.langchain.test_chat_model import TestResponseManager
from toolbox_test.base.mock.test_ai_manager import TestAIManager
from toolbox_test.base.tests.base_test import BaseTest
from toolbox_test.models.test_anthropic_overloaded_handler import MOCK_ANTHROPIC_OVERLOADED_RESPONSE


class TestGraphRunner(BaseTest):
    CONCEPT_LAYER_ID = "concepts"
    PET_LAYER_ID = "pets"
    FACTS_LAYER_ID = "facts"
    ARTIFACT_CONTENT = ["dogs", "cats",  # 0, 1
                        "Cat1: Michael", "Dog1: Scruffy", "Cat2: Meredith", "Dog2: Rocky",  # 2, 3, 4, 5
                        "Michael is quite fat", "Meredith bites a lot", "Rocky loves bubbles", "Scruffy has a toupee",  # 6, 7, 8, 9
                        "Cats are better than dogs"]  # 10
    ARTIFACT_IDS = [f"{i}" for i, _ in enumerate(ARTIFACT_CONTENT)]
    LAYER_IDS = [CONCEPT_LAYER_ID] * 2 + [PET_LAYER_ID] * 4 + [FACTS_LAYER_ID] * 5
    TRACES = {
        0: [3, 5, 10],
        1: [2, 4, 10],
        2: [6],
        3: [9],
        4: [7],
        5: [8],
    }
    QUESTION = "What pet should I get?"
    ANSWER = "Michael seems like the best option since cats are better than dogs and meredith bites a lot which is less preferable."
    REFERENCE_IDS = ["6", "7", "2", "10"]

    @mock_chat_model
    def test_full_generation(self, response_manager: TestResponseManager):
        first_res = RetrieveAdditionalInformation(retrieval_query="best pet")
        second_res = ExploreArtifactNeighborhood(artifact_ids=1, artifact_types="pets")
        third_res = ExploreArtifactNeighborhood(artifact_ids=[2, 4])
        repeat_res = RetrieveAdditionalInformation(retrieval_query="best pet")
        final_res = GenerateNode(self.get_args()).get_agent().create_response_obj([self.ANSWER, self.REFERENCE_IDS])
        response_manager.set_responses([first_res, second_res, third_res, repeat_res, final_res])
        answer_obj, runner = self.run_chat_test(response_manager)
        self.assertIsInstance(answer_obj, AnswerUser)
        self.assertEqual(answer_obj.answer, self.ANSWER)
        self.assertListEqual(answer_obj.reference_ids, self.REFERENCE_IDS)

        self.assert_state_history(runner)
        runner.clear_run_history()
        self.assertIsNone(runner.get_nodes_visited_on_last_run())
        self.assertIsNone(runner.get_states_from_last_run())

    @mock_anthropic
    @mock_chat_model
    def test_run_multi(self, response_manager: TestResponseManager, anthropicResponseManager: TestAIManager):
        first_res = RetrieveAdditionalInformation(retrieval_query="best pet")
        second_res = ExploreArtifactNeighborhood(artifact_ids=1, artifact_types="pets")
        third_res = ExploreArtifactNeighborhood(artifact_ids=[2, 4])
        repeat_res = RetrieveAdditionalInformation(retrieval_query="best pet")
        final_res = GenerateNode(self.get_args()).get_agent().create_response_obj([self.ANSWER, self.REFERENCE_IDS])
        request_assistance = RequestAssistance()
        internal_server_error = InternalServerError(message="This is the message",
                                                    response=httpx.Response(
                                                        status_code=529,
                                                        json=MOCK_ANTHROPIC_OVERLOADED_RESPONSE,
                                                        request=MagicMock(spec=httpx.Request)
                                                    ),
                                                    body=MOCK_ANTHROPIC_OVERLOADED_RESPONSE)
        responses = {"1": [first_res, second_res, third_res, repeat_res, final_res], "2": [request_assistance], "3": ["I dont know."],
                     "4": [Exception], "5": [internal_server_error, final_res]}
        response_manager.set_responses(responses)
        anthropicResponseManager.set_responses(["I'm alive!"])  # for overloaded check

        questions = [self.QUESTION, "This is a really hard question?", "What is the meaning of life?", "failure", "rate limited"]
        runner = GraphRunner(self.get_definition())
        args = self.get_args()
        args.user_question = None
        outputs = runner.run_multi(args, user_question=questions, thread_ids=list(responses.keys()))
        answer_obj = outputs[0]
        self.assertEqual(answer_obj.answer, self.ANSWER)
        self.assertListEqual(answer_obj.reference_ids, self.REFERENCE_IDS)

        assistance_obj = outputs[1]
        self.assertEqual(assistance_obj.relevant_information_learned, request_assistance.relevant_information_learned)

        bad_response = outputs[2]
        self.assertIsNone(bad_response)

        bad_response = outputs[3]
        self.assertIsNone(bad_response)

        second_attempt_answer = outputs[4]
        self.assertEqual(second_attempt_answer.answer, self.ANSWER)
        self.assertListEqual(second_attempt_answer.reference_ids, self.REFERENCE_IDS)

        self.assert_state_history(runner)

    @mock_chat_model
    def test_with_failure(self, response_manager: TestResponseManager):
        first_res = RetrieveAdditionalInformation(retrieval_query="best pet")
        second_res = ExploreArtifactNeighborhood(artifact_ids=1, artifact_types="pets")
        response_manager.set_responses([first_res, second_res, first_res, second_res, "I dont know"])
        answer_obj, runner = self.run_chat_test(response_manager)
        self.assertIsNone(answer_obj)

    @mock_chat_model
    def test_with_request_assistance(self, response_manager: TestResponseManager):
        first_res = RetrieveAdditionalInformation(retrieval_query="best pet")
        final_res = RequestAssistance()
        response_manager.set_responses([first_res, final_res])
        answer_obj, runner = self.run_chat_test(response_manager)
        self.assertIsInstance(answer_obj, RequestAssistance)
        self.assertEqual(answer_obj.relevant_information_learned, final_res.relevant_information_learned)
        self.assertEqual(answer_obj.related_doc_ids, final_res.related_doc_ids)

    def assert_state_history(self, runner: GraphRunner, run_num: int = 0):
        generate_node = SupportedNodes.GENERATE.name
        retrieve_node = SupportedNodes.RETRIEVE.name
        explore_node = SupportedNodes.EXPLORE_NEIGHBORS.name
        continue_node = SupportedNodes.CONTINUE.name
        self.assertListEqual(runner.nodes_visited_on_runs[run_num],
                             [START, generate_node, retrieve_node, generate_node, explore_node,
                              generate_node, explore_node, generate_node,
                              generate_node, continue_node])
        self.assertEqual(runner.states_for_runs[run_num][-1]['generation'], self.ANSWER)

    def run_chat_test(self, response_manager: TestResponseManager):
        args = self.get_args()
        runner = GraphRunner(self.get_definition())
        answer_obj = runner.run(args)
        return answer_obj, runner

    def get_definition(self):
        return GraphDefinition(
            nodes=[
                SupportedNodes.GENERATE,
                SupportedNodes.RETRIEVE,
                SupportedNodes.CONTINUE,
                SupportedNodes.EXPLORE_NEIGHBORS
            ],
            edges=[
                Edge(SupportedNodes.GENERATE, SupportedBranches.DECIDE_NEXT),
                Edge(SupportedNodes.CONTINUE, SupportedNodes.END_COMMAND),
                Edge(SupportedNodes.RETRIEVE, SupportedNodes.GENERATE),
                Edge(SupportedNodes.EXPLORE_NEIGHBORS, SupportedNodes.GENERATE)],
            state_type=GraphState,
            output_converter=self.converter())

    def converter(self):
        paths = [Path(condition=GraphStateVars.GENERATION.exists(),
                      action=lambda state: AnswerUser(answer=GraphStateVars.GENERATION.get_value(state),
                                                      reference_ids=GraphStateVars.REFERENCE_IDS.get_value(state))),
                 Path(condition=GraphStateVars.RELEVANT_INFORMATION.exists(),
                      action=lambda state: RequestAssistance(
                          relevant_information_learned=GraphStateVars.RELEVANT_INFORMATION.get_value(state),
                          related_doc_ids=GraphStateVars.RELATED_DOC_IDS.get_value(state))),
                 Path(action=None)
                 ]
        return PathSelector(*paths)

    def construct_dataset(self):
        trace_df = TraceDataFrame([{TraceKeys.child_label(): str(child), TraceKeys.parent_label(): str(parent), TraceKeys.LABEL: 1}
                                   for parent, children in self.TRACES.items() for child in children])
        artifact_df = ArtifactDataFrame([Artifact(id=self.ARTIFACT_IDS[i], content=content,
                                                  layer_id=self.LAYER_IDS[i]) for i, content in enumerate(self.ARTIFACT_CONTENT)])
        layer_df = LayerDataFrame([{LayerKeys.SOURCE_TYPE: self.PET_LAYER_ID, LayerKeys.TARGET_TYPE: self.CONCEPT_LAYER_ID},
                                   {LayerKeys.SOURCE_TYPE: self.FACTS_LAYER_ID, LayerKeys.TARGET_TYPE: self.PET_LAYER_ID}
                                   ])
        trace_dataset = TraceDataset(artifact_df, trace_df, layer_df)
        prompt_dataset = PromptDataset(trace_dataset=trace_dataset)
        return prompt_dataset

    def get_args(self):
        args = GraphArgs(user_question=self.QUESTION, dataset=self.construct_dataset())
        return args

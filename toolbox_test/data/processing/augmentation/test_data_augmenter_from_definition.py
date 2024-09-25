from toolbox.data.processing.augmentation.data_augmenter import DataAugmenter
from toolbox.infra.experiment.variables.experimental_variable import ExperimentalVariable
from toolbox_test.base.object_definitions import TestObjectDefinitions
from toolbox_test.base.tests.base_test import BaseTest


class TestDataAugmenterFromDefinition(BaseTest):
    def test_basic(self):
        definition = {
            "steps": []
        }
        data_augmenter = TestObjectDefinitions.create(DataAugmenter, override=True, **definition)
        self.assertEqual(len(data_augmenter.steps), 0)

    def test_one_step(self):
        definition = {
            "steps": [
                {
                    "object_type": "SOURCE_TARGET_SWAP"
                }
            ]
        }
        data_augmenter = TestObjectDefinitions.create(DataAugmenter, override=True, **definition)
        self.assertEqual(len(data_augmenter.steps), 1)

    def test_experiment(self):
        data_augmenters: ExperimentalVariable = TestObjectDefinitions.create(DataAugmenter)
        n_a = len(data_augmenters[0].steps)
        n_b = len(data_augmenters[1].steps)
        self.assertEqual(n_a, 0)
        self.assertEqual(n_b, 1)

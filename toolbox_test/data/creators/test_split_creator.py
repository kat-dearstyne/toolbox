from toolbox.data.creators.split_dataset_creator import SplitDatasetCreator
from toolbox_test.base.tests.base_test import BaseTest


class TestSplitDatasetCreator(BaseTest):
    def test_val_percentage_error(self):
        with self.assertRaises(ValueError) as e:
            SplitDatasetCreator(val_percentage=2)
        self.assertIn("cannot be more than 1.", str(e.exception))

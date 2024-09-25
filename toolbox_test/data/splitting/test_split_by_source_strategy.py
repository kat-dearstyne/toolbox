from toolbox.data.splitting.supported_split_strategy import SupportedSplitStrategy
from toolbox_test.base.tests.base_split_test import BaseSplitTest


class TestRandomAllSourcesSplit(BaseSplitTest):
    """
    Responsible for testing that data splitting references all sources
    """

    def test_split_sizes(self):
        split_type = SupportedSplitStrategy.SPLIT_BY_SOURCE
        self.assert_split_multiple(split_type)

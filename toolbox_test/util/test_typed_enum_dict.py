from toolbox.data.objects.trace import Trace
from toolbox.data.keys.structure_keys import TraceKeys
from toolbox_test.base.tests.base_test import BaseTest


class TestTypedEnumDict(BaseTest):

    def test_trace(self):
        trace = Trace(link_id=1, source="source", target="target", score=0.5, label=1, explanation="explanation")
        source = trace.get(TraceKeys.SOURCE)
        self.assertEqual(source, "source")

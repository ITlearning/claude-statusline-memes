import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import context_budget as cb


class TestShouldWarn(unittest.TestCase):
    def test_above_threshold(self):
        self.assertTrue(cb.should_warn(85, 80))
    def test_at_threshold(self):
        self.assertTrue(cb.should_warn(80, 80))
    def test_below_threshold(self):
        self.assertFalse(cb.should_warn(79.9, 80))
    def test_none(self):
        self.assertFalse(cb.should_warn(None, 80))
    def test_bad_value(self):
        self.assertFalse(cb.should_warn("oops", 80))


if __name__ == '__main__':
    unittest.main()

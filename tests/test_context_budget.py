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


import json, tempfile, shutil


class TestCountMessages(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.tx = os.path.join(self.dir, 'transcript.jsonl')
        self.cache = os.path.join(self.dir, 'cache.json')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, rows):
        with open(self.tx, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')

    def test_counts_user_and_assistant_excludes_meta(self):
        self._write([
            {"type": "user", "message": {"content": "hi"}},
            {"type": "assistant", "message": {"content": []}},
            {"type": "user", "isMeta": True, "message": {"content": "meta"}},
            {"type": "summary"},
            {"type": "user", "message": {"content": "again"}},
        ])
        self.assertEqual(cb.count_messages(self.tx, self.cache), 3)

    def test_missing_file_returns_none(self):
        self.assertIsNone(cb.count_messages(self.dir + '/nope.jsonl', self.cache))
        self.assertIsNone(cb.count_messages(None, self.cache))

    def test_uses_cache_when_mtime_unchanged(self):
        self._write([{"type": "user", "message": {"content": "hi"}}])
        first = cb.count_messages(self.tx, self.cache)
        self.assertEqual(first, 1)
        mtime = os.stat(self.tx).st_mtime
        with open(self.cache, 'w') as f:
            json.dump({self.tx: {"mtime": mtime, "count": 999}}, f)
        self.assertEqual(cb.count_messages(self.tx, self.cache), 999)


if __name__ == '__main__':
    unittest.main()

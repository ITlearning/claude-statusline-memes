import os, sys, json, tempfile, shutil, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import checkpoint as ck


class TestSlug(unittest.TestCase):
    def test_path_encoded(self):
        self.assertEqual(ck.slug_for('/Users/tabber/ios-studio'), 'Users-tabber-ios-studio')
    def test_empty(self):
        self.assertEqual(ck.slug_for(''), 'unknown')


class TestExtractLastPrompt(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.tx = os.path.join(self.dir, 't.jsonl')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, rows):
        with open(self.tx, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')

    def test_returns_last_real_skips_noise(self):
        self._write([
            {"type": "user", "message": {"content": "first real"}},
            {"type": "user", "message": {"content": "<command-name>/clear</command-name>"}},
            {"type": "user", "isMeta": True, "message": {"content": "meta"}},
            {"type": "assistant", "message": {"content": []}},
            {"type": "user", "message": {"content": "second real"}},
            {"type": "user", "message": {"content": "<bash-stdout>x</bash-stdout>"}},
        ])
        self.assertEqual(ck.extract_last_prompt(self.tx), 'second real')

    def test_truncates(self):
        self._write([{"type": "user", "message": {"content": "x" * 500}}])
        self.assertEqual(len(ck.extract_last_prompt(self.tx, maxlen=200)), 200)

    def test_missing(self):
        self.assertEqual(ck.extract_last_prompt(None), '')
        self.assertEqual(ck.extract_last_prompt(self.dir + '/nope'), '')


if __name__ == '__main__':
    unittest.main()

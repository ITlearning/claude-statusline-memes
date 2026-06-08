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


class TestBuildAndRun(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.cp = os.path.join(self.dir, 'checkpoints')
        self.tx = os.path.join(self.dir, 't.jsonl')
        with open(self.tx, 'w') as f:
            f.write(json.dumps({"type": "user", "message": {"content": "do the thing"}}) + '\n')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_build_block_has_fields(self):
        block = ck.build_block('2026-06-08T08:55Z', 'auto', '/x', 'main', 'abc1234',
                               'sess1', 'hello', '/t.jsonl')
        self.assertIn('## 2026-06-08T08:55Z · auto · /x', block)
        self.assertIn('branch: main (HEAD abc1234)', block)
        self.assertIn('session: sess1', block)
        self.assertIn('last prompt: "hello"', block)
        self.assertIn('transcript: /t.jsonl', block)

    def test_run_writes_checkpoint(self):
        data = {"cwd": self.dir, "transcript_path": self.tx,
                "session_id": "s1", "trigger": "manual"}
        path = ck.run(data, '2026-06-08T09:00Z', self.cp)
        self.assertTrue(os.path.exists(path))
        body = open(path).read()
        self.assertIn('· manual · ' + self.dir, body)
        self.assertIn('last prompt: "do the thing"', body)

    def test_run_handles_non_git_cwd_and_missing_trigger(self):
        data = {"cwd": self.dir, "transcript_path": self.tx, "session_id": "s2"}
        path = ck.run(data, '2026-06-08T09:01Z', self.cp)
        body = open(path).read()
        self.assertIn('· compact · ', body)
        self.assertIn('branch: ?', body)

    def test_run_appends(self):
        data = {"cwd": self.dir, "transcript_path": self.tx, "session_id": "s3"}
        p1 = ck.run(data, '2026-06-08T09:02Z', self.cp)
        ck.run(data, '2026-06-08T09:03Z', self.cp)
        self.assertEqual(open(p1).read().count('## '), 2)


if __name__ == '__main__':
    unittest.main()

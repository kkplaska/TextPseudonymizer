import unittest
from app.engine import anonymize_text, deanonymize_text

class TestEngine(unittest.TestCase):
    def test_basic_anonymize_and_deanonymize(self):
        text = "Hello John Doe, your email is john@example.com."
        words = ["John Doe", "john@example.com"]
        
        anon_text, mapping = anonymize_text(text, words)
        
        # Check mapping
        self.assertIn("John Doe", mapping)
        self.assertIn("john@example.com", mapping)
        self.assertNotIn("John Doe", anon_text)
        self.assertNotIn("john@example.com", anon_text)
        
        # Restore
        restored = deanonymize_text(anon_text, mapping)
        self.assertEqual(restored, text)

    def test_whole_words_matching_true(self):
        text = "axyzb and a-xyz-b and xyz"
        words = ["xyz"]
        
        anon_text, mapping = anonymize_text(text, words, match_whole_words=True)
        
        # axyzb should not be replaced, but a-xyz-b and standalone xyz should
        self.assertTrue(anon_text.startswith("axyzb"))
        token = mapping["xyz"]
        self.assertIn(f"a-{token}-b", anon_text)
        self.assertTrue(anon_text.endswith(token))

    def test_whole_words_matching_false(self):
        text = "axyzb and a-xyz-b and xyz"
        words = ["xyz"]
        
        anon_text, mapping = anonymize_text(text, words, match_whole_words=False)
        
        # All occurrences including inside axyzb should be replaced
        self.assertNotIn("xyz", anon_text)
        token = mapping["xyz"]
        self.assertEqual(anon_text, f"a{token}b and a-{token}-b and {token}")

    def test_existing_mapping_reuse(self):
        text = "First name is Alice, second is Bob."
        words = ["Alice", "Bob"]
        existing_mapping = {"Alice": "<[ANON_PREV]>"}
        
        anon_text, mapping = anonymize_text(text, words, existing_mapping=existing_mapping)
        
        # Alice should use the existing token
        self.assertEqual(mapping["Alice"], "<[ANON_PREV]>")
        self.assertIn("<[ANON_PREV]>", anon_text)
        # Bob should receive a new token
        self.assertIn("Bob", mapping)
        self.assertNotEqual(mapping["Bob"], "<[ANON_PREV]>")

    def test_polish_diacritics_and_special_chars(self):
        text = "Zażółć gęślą jaźń $variable.myMethod() { return true; }"
        words = ["Zażółć gęślą", "$variable.myMethod()"]
        
        anon_text, mapping = anonymize_text(text, words)
        
        self.assertNotIn("Zażółć gęślą", anon_text)
        self.assertNotIn("$variable.myMethod()", anon_text)
        
        restored = deanonymize_text(anon_text, mapping)
        self.assertEqual(restored, text)

    def test_large_text_performance(self):
        # Generate ~70,000 character script
        line = 'def processUser() { println "Processing record: user_secret_123" }\n'
        text = line * 1000
        words = ["processUser", "user_secret_123"]
        
        anon_text, mapping = anonymize_text(text, words)
        
        self.assertNotIn("processUser", anon_text)
        self.assertNotIn("user_secret_123", anon_text)
        self.assertEqual(len(mapping), 2)
        
        restored = deanonymize_text(anon_text, mapping)
        self.assertEqual(restored, text)

if __name__ == "__main__":
    unittest.main()

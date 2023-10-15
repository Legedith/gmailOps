import unittest


class TestRuleEvaluation(unittest.TestCase):
    def test_rule_evaluate_contains(self):
        rule = Rule("From", "contains", "example.com")
        email = {"From": "user@example.com"}
        self.assertTrue(rule.evaluate(email))

    def test_rule_evaluate_does_not_contain(self):
        rule = Rule("From", "does not contain", "example.com")
        email = {"From": "user@example.org"}
        self.assertTrue(rule.evaluate(email))

    # Add more test cases for different scenarios

class TestRuleCollectionEvaluation(unittest.TestCase):
    def test_rule_collection_all(self):
        rule1 = Rule("From", "contains", "example.com")
        rule2 = Rule("Subject", "contains", "important")
        rule_collection = RuleCollection({
            "rule_name": "Test Rule",
            "rule_type": "All",
            "rules": [rule1, rule2]
        })
        email = {"From": "user@example.com", "Subject": "Important email"}
        self.assertTrue(rule_collection.evaluate(email))

    def test_rule_collection_any(self):
        rule1 = Rule("From", "contains", "example.com")
        rule2 = Rule("Subject", "contains", "important")
        rule_collection = RuleCollection({
            "rule_name": "Test Rule",
            "rule_type": "Any",
            "rules": [rule1, rule2]
        })
        email1 = {"From": "user@example.org", "Subject": "Not important"}
        email2 = {"From": "user@example.com", "Subject": "Not important"}
        self.assertTrue(rule_collection.evaluate(email1))
        self.assertTrue(rule_collection.evaluate(email2))

    # Add more test cases for different scenarios

if __name__ == '__main__':
    unittest.main()

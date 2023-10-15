import unittest
from gmailOps import Rule, RuleCollection

class TestRuleEvaluation(unittest.TestCase):
    # Since From, Subject, and Message are all strings, we can test them together
    def test_rule_evaluate_contains(self):
        rule = Rule("From", "contains", "example.com")
        email = {"From": "user@example.com"}
        self.assertTrue(rule.evaluate(email))

    def test_rule_evaluate_does_not_contain(self):
        rule = Rule("From", "does not contain", "example.com")
        email = {"From": "user@example.org"}
        self.assertTrue(rule.evaluate(email))

    def test_rule_evaluate_equals(self):
        rule = Rule("From", "equals", "hello@123")
        email = {"From": "hello@123"}
        self.assertTrue(rule.evaluate(email))
    
    def test_rule_evaluate_does_not_equal(self):
        rule = Rule("From", "not equals", "hello@123")
        email = {"From": "hello@1234"}
        self.assertTrue(rule.evaluate(email))

    def test_rule_evaluate_less_than(self):
        rule = Rule("Received Date/Time", "less than", "1 D")
        email = {"Received Date/Time": "Thu, 01 Jan 1970 00:00:00 +0000"}
        self.assertFalse(rule.evaluate(email))

    def test_rule_evaluate_greater_than(self):
        rule = Rule("Received Date/Time", "greater than", "1 D")
        email = {"Received Date/Time": "Thu, 01 Jan 1970 00:00:00 +0000"}
        self.assertTrue(rule.evaluate(email))


if __name__ == '__main__':
    unittest.main()

class Rule:
    def __init__(self, field, predicate, value):
        self.field = field
        self.predicate = predicate
        self.value = value

    def evaluate(self, email):
        if self.field == "From":
            field_value = email.get("From", "")
        elif self.field == "Subject":
            field_value = email.get("Subject", "")
        elif self.field == "Message":
            field_value = email.get("Message", "")
        elif self.field == "Received Date/Time":
            field_value = email.get("Received Date/Time", "")
        else:
            return False  # Field not supported

        if self.field in ["From", "Subject", "Message"]:
            if self.predicate == "contains":
                return self.value in field_value
            elif self.predicate == "does not contain":
                return self.value not in field_value
            elif self.predicate == "equals":
                return field_value == self.value
            elif self.predicate == "not equals":
                return field_value != self.value

        elif self.field == "Received Date/Time":
            if self.predicate == "less than":
                return field_value < self.value
            elif self.predicate == "greater than":
                return field_value > self.value

        else:
            return False  # Predicate not supported


class RuleCollection:
    def __init__(self, rule_data):
        self.rule_name = rule_data.get("rule_name", "")
        self.rule_description = rule_data.get("rule_description", "")
        self.rule_type = rule_data.get("rule_type", "")
        self.actions = rule_data.get("actions", [])
        self.rules = [Rule(rule['field'], rule['predicate'], rule['value']) for rule in rule_data.get("rules", [])]

    def evaluate(self, email):
        check_func = all if self.rule_type == "All" else any
        if check_func(rule.evaluate(email) for rule in self.rules):
            self.execute_actions(email)
            return True
        return False

    def execute_actions(self, email):
        for action in self.actions:
            action_type = action["action_type"]
            action_value = action["action_value"]
            if action_type == "mark":
                self.mark(email, action_value)
            elif action_type == "move":
                self.move(email, action_value)

    def mark(self, email, action_value):
        # Replace this with your actual marking logic
        print(f"Marking email with ID: {email['ID']} as {action_value}")

    def move(self, email, action_value):
        # Replace this with your actual moving logic
        print(f"Moving email with ID: {email['ID']} to folder: {action_value}")



# Example rule data following the schema
example_rule_data = {
    "rule_name": "Mark Unread - Jatin",
    "rule_description": "Mark unread emails from this cool guy Jatin.",
    "rule_type": "All",
    "rules": [
        {
            "field": "From",
            "predicate": "equals",
            "value": "21mcmc01@uohyd.ac.in"
        }
    ],
    "actions": [
        {
            "action_type": "mark",
            "action_value": "unread"
        }
    ]
}

# Create a RuleCollection object from the example rule data
rule_collection = RuleCollection(example_rule_data)

# Simulate an email object
email = {
    "ID": 123,
    "From": "21mcmc01@uohyd.ac.in",
    "Subject": "Important Email",
    "Message": "This is the email content.",
    "Received Date/Time": "2023-10-13 10:30:00"
}

# Check if the email matches the rule
if rule_collection.evaluate(email):
    print(f"The email meets the rule: {rule_collection.rule_name}")
    
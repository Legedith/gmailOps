import json

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

        # - For string type fields - Contains, Does not Contain, Equals, Does not equal
        if self.field in ["From", "Subject", "Message"]:
            if self.predicate == "contains":
                return self.value in field_value
            elif self.predicate == "does not contain":
                return self.value not in field_value
            elif self.predicate == "equals":
                return field_value == self.value
            elif self.predicate == "not equals":
                return field_value != self.value
        
        # - For date type field (Received) - Less than / Greater than for days / months
        elif self.field == "Received Date/Time":
            if self.predicate == "less than":
                return field_value < self.value
            elif self.predicate == "greater than":
                return field_value > self.value
            
        else:
            return False  # Predicate not supported

class RuleCollection:
    def __init__(self, rules, rule_type):
        self.rules = [Rule(rule['field'], rule['predicate'], rule['value']) for rule in rules]
        self.rule_type = rule_type

    def evaluate(self, email):
        if self.rule_type == "All":
            return all(rule.evaluate(email) for rule in self.rules)
        elif self.rule_type == "Any":
            return any(rule.evaluate(email) for rule in self.rules)
        else:
            return False  # Rule type not supported

# to test:
import sqlite3

def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('email_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails")
    rows = cursor.fetchall()

    rules = []  # Store rule instances here

    # Load rules from a JSON file and create rule instances
    with open("rules.json", "r") as json_file:
        rule_data = json.load(json_file)
        rules = [RuleCollection(rule_data['rules'], rule_data['rule_type'])]

    # Simulate email objects using database rows
    for row in rows:
        email = {
            "ID": row[0],
            "From": row[1],
            "Subject": row[2],
            # Add other fields as needed
        }

        # Check the email against each rule
        for rule_collection in rules:
            if rule_collection.evaluate(email):
                # Perform the appropriate action based on the rule
                for rule in rule_collection.rules:
                    if rule.predicate == "mark":
                        rule.mark(email)
                    elif rule.predicate == "move":
                        rule.move(email)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()

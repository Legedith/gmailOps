import argparse
import sqlite3
import json
import pytz
from datetime import datetime, timedelta


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

        # Subject or Message can be empty
        if self.field in ["From", "Subject", "Message"] and field_value:
            # Not accounting for case sensitivity
            if self.predicate == "contains":
                return self.value.lower() in field_value.lower()
            elif self.predicate == "does not contain":
                return self.value.lower() not in field_value.lower()
            elif self.predicate == "equals":
                return field_value.lower() == self.value.lower()
            elif self.predicate == "not equals":
                return field_value.lower() != self.value.lower()

        elif self.field == "Received Date/Time":
            date_formats = ["%a, %d %b %Y %H:%M:%S %z",
                            "%d %b %Y %H:%M:%S %z (UTC)"]

            for format in date_formats:
                date_str = email.get(
                    "Received Date/Time").replace(" (UTC)", "")
                # print(date_str)
                try:
                    email_date = datetime.strptime(date_str, format)
                    break
                except Exception as e:
                    print(f"Error parsing date: {e}")
                    return False

            value_parts = self.value.split()
            num = int(value_parts[0])
            unit = value_parts[1]
            # print(datetime.now(pytz.UTC))
            if unit == "D":
                comparison_date = datetime.now(pytz.UTC) - timedelta(days=num)
            elif unit == "M":
                comparison_date = datetime.now(
                    pytz.UTC) - timedelta(days=num * 30)

            # print(email_date, comparison_date)
            if self.predicate == "less than":
                return email_date >= comparison_date
            elif self.predicate == "greater than":
                return email_date < comparison_date
        else:
            return False  # Predicate not supported


class RuleCollection:
    def __init__(self, rule_data):
        self.rule_name = rule_data.get("rule_name", "")
        self.rule_description = rule_data.get("rule_description", "")
        self.rule_type = rule_data.get("rule_type", "")
        self.actions = rule_data.get("actions", [])
        self.rules = [Rule(rule['field'], rule['predicate'], rule['value'])
                      for rule in rule_data.get("rules", [])]

    def evaluate(self, email):
        check_func = all if self.rule_type.lower() == "all" else any
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
        from fetch import authenticate_gmail
        from googleapiclient.discovery import build
        # Use the Gmail API to mark the email
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        # Retrieve the email ID from your email data
        email_id = email['ID']

        # Implement your marking logic here
        if action_value == "read":
            # Mark the email as read
            service.users().messages().modify(userId='me', id=email_id, body={
                'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute()
            print(f"Marked email with ID: {email_id} as read")
            # print email subject
            # print(f"Email subject: {email['Subject']}")
        elif action_value == "unread":
            # Mark the email as unread
            service.users().messages().modify(userId='me', id=email_id, body={
                'removeLabelIds': [], 'addLabelIds': ['UNREAD']}).execute()
            print(f"Marked email with ID: {email_id} as unread")
        else:
            print(f"Invalid action: {action_value}. No action taken.")

    def move(self, email, action_value):
        from fetch import authenticate_gmail
        from googleapiclient.discovery import build
        # Use the Gmail API to mark the email
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        # Retrieve the email ID from your email data
        email_id = email['ID']

        # Implement your moving logic here
        # For example, you can use the 'users().messages().modify()' method to add a label to the email.
        # Replace 'Label_ID' with the actual label you want to use.
        label_id = action_value
        service.users().messages().modify(userId='me', id=email_id,
                                          body={'addLabelIds': [label_id]}).execute()

        print(f"Moved email with ID: {email_id} to folder: {action_value}")
        # Print email subject
        # print(f"Email subject: {email['Subject']}")


def main():
    parser = argparse.ArgumentParser(
        description="Process emails using rules from a JSON file.")
    parser.add_argument("json_file", nargs="?", default="./rules/Happy_Fox.json",
                        help="Path to the JSON file containing rules (default: ./rules/Happy_Fox.json)")

    args = parser.parse_args()

    # Load rules from the specified JSON file and create rule instances
    rules = []

    with open(args.json_file, "r") as json_file:
        rule_data = json.load(json_file)
        rules.append(RuleCollection(rule_data))

    # Simulate email objects using database rows
    # Connect to the SQLite database
    conn = sqlite3.connect('email_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails")
    rows = cursor.fetchall()

    for row in rows:
        email = {
            "ID": row[0],
            "From": row[1],
            "Subject": row[2],
            "Message": row[3],  # Include the "Message" field
            # Include the "Received Date/Time" field
            "Received Date/Time": row[4],
        }
        # print(email['Subject'])

        # Check the email against each rule
        for rule_collection in rules:
            try:
                rule_collection.evaluate(email)
            except Exception as e:
                print(f"Error evaluating email: {e}")
                print(f"Email: {email}")

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    main()

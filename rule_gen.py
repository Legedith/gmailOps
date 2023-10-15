import json

def create_rule(rule_name, rule_description, rule_type, fields, actions):
    rule = {
        "rule_name": rule_name,
        "rule_description": rule_description,
        "rule_type": rule_type,
        "rules": fields,
        "actions": actions
    }
    return rule

def prompt_for_field():
    print("Select a field:")
    print("1. From")
    print("2. Subject")
    print("3. Message")
    print("4. Received Date/Time")
    field_mapping = {
        "1": "From",
        "2": "Subject",
        "3": "Message",
        "4": "Received Date/Time"
    }
    while True:
        field_choice = input("Enter the field number: ")
        if field_choice in field_mapping:
            return field_mapping[field_choice]
        else:
            print("Invalid field number. Please try again.")

def prompt_for_predicate(field):
    allowed_predicates = {
        "From": ["contains", "does not contain", "equals", "does not equal"],
        "Subject": ["contains", "does not contain", "equals", "does not equal"],
        "Message": ["contains", "does not contain", "equals", "does not equal"],
        "Received Date/Time": ["less than", "greater than"]
    }
    print(f"Select a predicate for the '{field}' field:")
    for i, predicate in enumerate(allowed_predicates[field], start=1):
        print(f"{i}. {predicate}")
    while True:
        predicate_choice = input("Enter the predicate number: ")
        if predicate_choice.isdigit() and int(predicate_choice) in range(1, len(allowed_predicates[field]) + 1):
            return allowed_predicates[field][int(predicate_choice) - 1]
        else:
            print("Invalid predicate number. Please try again.")

def prompt_for_value(field):
    if field == "Received Date/Time":
        print("Select a time unit:")
        print("1. Days")
        print("2. Months")
        time_units = ["Days", "Months"]
        while True:
            unit_choice = input("Enter the unit number: ")
            if unit_choice in ["1", "2"]:
                unit = time_units[int(unit_choice) - 1]
                value = input(f"Enter the number of {unit}: ")
                return f"{value} {unit[0]}"  # Convert "Days" to "D" and "Months" to "M"
            else:
                print("Invalid unit number. Please try again.")
    else:
        return input(f"Enter the field value for '{field}': ")

def prompt_for_action():
    print("Select an action:")
    print("1. Mark as Read")
    print("2. Mark as Unread")
    print("3. Move to Label")
    def prompt_for_label_id():
        return input("Enter the label ID: ")
    action_mapping = {
        "1": {"action_type": "mark", "action_value": "read"},
        "2": {"action_type": "mark", "action_value": "unread"},
        "3": {"action_type": "move", "action_value": ""}
    }
    while True:
        action_choice = input("Enter the action number: ")
        if action_choice in action_mapping:
            if action_choice == "3":
                action_mapping[action_choice]["action_value"] = prompt_for_label_id()
            return action_mapping[action_choice]
        else:
            print("Invalid action number. Please try again.")

def main():
    rule_name = input("Enter the rule name: ")
    rule_description = input("Enter the rule description: ")
    rule_type = input("Enter the rule type (Any/All): ")

    fields = []
    while True:
        field_name = prompt_for_field()
        predicate = prompt_for_predicate(field_name)
        field_value = prompt_for_value(field_name)

        field = {
            "field": field_name,
            "predicate": predicate,
            "value": field_value
        }
        fields.append(field)

        another_field = input("Add another field? (yes/no): ")
        if another_field.lower() != "yes":
            break

    actions = []
    while True:
        action = prompt_for_action()
        actions.append(action)

        another_action = input("Add another action? (yes/no): ")
        if another_action.lower() != "yes":
            break

    rule = create_rule(rule_name, rule_description, rule_type, fields, actions)
    rule_json = json.dumps(rule, indent=2)

    # Save the rule as a JSON file with spaces replaced by underscores
    file_name = f"{rule_name.replace(' ', '_')}.json"
    with open(file_name, "w") as json_file:
        json_file.write(rule_json)

    print(f"Rule saved as {file_name}")


if __name__ == "__main__":
    main()

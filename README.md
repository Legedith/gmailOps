
## Installation

There are two ways to set up the project:

1. **Using Provided Project**: In this case, you can request access to my project, where I will share OAuth client credentials and add your email as a tester. Once granted access, you'll be able to use the provided credentials for API access.

2. **Setting Up Your Own Project**:
   - Go to the [Google Cloud Console](https://developers.google.com/workspace/guides/get-started).
   - Create a project and set up the necessary credentials for Gmail API access. You should have these credentials downloaded to your system and placed in the same folder as this repository.

Once you have your credentials ready, proceed with the following steps:

1. **Python Virtual Environment**:
   - Create a Python virtual environment to keep your dependencies isolated.
   - Install the required packages using `pip`:
     ```bash
     pip install -r requirements.txt
     ```

2. **Test Gmail API Access**:
   - Run the following command to check that you can access the Gmail API:
     ```bash
     python ./helper_scripts/labelHelper.py
     ```
   - This script will display the labels in your email account, along with their IDs. If you haven't previously authorized access, it will guide you through the sign-in process and create a `token.json` file in your folder.

3. **Create Rules**:
   - Use the interactive command-line tool to create rules for email processing:
     ```bash
     python helper_scripts/rule_gen.py
     ```
   - The generated rule schema will look like this:
     ```json
     {
       "rule_name": "",
       "rule_description": "",
       "rule_type": "Any/All",
       "rules": [
         {
           "field": "From, Subject, Message, Received Date/Time",
           "predicate": "- For string type fields - Contains, Does not Contain, Equals, Does not equal
                         - For date type field (Received) - Less than / Greater than for days / months.",
           "value": ""
         }
       ],
       "actions": [
         {
           "action_type": "mark",
           "action_value": "read"
         },
         {
           "action_type": "move",
           "action_value": "Label_ID"
         }
       ]
     }
     ```

4. **Fetch and Process Emails**:
   - Use the `fetch.py` script to retrieve emails from your account, which will be stored in a SQLite3 database.
   - Process these emails using the `gmailOps.py` script with your created rules. Usage:
     ```bash
     python gmailOps.py <rules_file>
     ```
   - The script will automatically perform the actions defined in the rule.

That's it! You are now set up to fetch and process emails according to your rules.

p.s. The `helper_scripts/testing.py` script has some rudimentary unit tests to test our rules.
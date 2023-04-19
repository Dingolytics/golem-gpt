KNOWN_ACTIONS_PROMT = """
You can use the following actions, earlier in the list - the higher priority:

- http_api_request(url, method, headers, data)
- parse_json(text)
- ask_golem(role, subgoal)
- search_google(query)
- read_file(path)
- write_file(path, content)
- get_datetime()
- ask_human(text)
- finish_job(message)

Always find a corresponding actions from the list above.
""".strip()

KNOWN_ROLES_PROMT = """
When asking a golem with the "ask_golem" action, decompose a goal into
particular tasks for experts expert roles are available:

- "coder" can create function with defined parameters and return value
- "devops" can create configuration files for deployment
- "admin" can install software on current machine
- "webdesigner" can create HTML page and save it to the file
- "artist" can create image and save it to the file
- "reviewer" can review the code or action and give feedback
"""

OUTPUT_FORMAT_PROMPT = """
You have to use the strict format for answers (JSON list of actions),
so robots can understand you. Never answer with a plain text.

Format:

[ {"action_1": {"parameters1": "value1"}},
  {"action_2": {"parameters2": "value2"}} ]
""".strip()

FINISH_PROMPT = "If job is finished, say 'finish_job'."

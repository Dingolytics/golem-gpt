KNOWN_ACTIONS_PROMT = """
You can use the following actions, higher in the list means the higher priority:

- ask_human_input(query)
- read_file(filename)
- write_file(filename, contents)
- http_request(url, method, headers, body, to_filename)
- create_python_script(name, description, in_files, out_files)
- create_shell_script(name, description, in_files, out_files)
- run_script(name)
- ask_google(query, to_filename)
- delegate_job(goal, role, in_files, out_files)
- explain(description)
- reject_job(message)
- finish_job(message)

Use explain() action to briefly describe what you are doing.

Always find a corresponding actions from the list above.
""".strip()

KNOWN_ROLES_PROMT = """
When using a the "delegate_job" action, assume the following roles:

- "coder" can create function with defined goal, inputs and outputs
- "admin" can install software on current machine
""".strip()

# - "devops" can create configuration files for deployment
# - "webdesigner" can create HTML page and save it to the file
# - "artist" can create image and save it to the file
# - "reviewer" can review the code or action and provide feedback

# OUTPUT_FORMAT_PROMPT = """
# You have to use the strict format for answers (JSON list of actions),
# so robots can understand you. Never answer with a plain text.

# Format:

# [{"action_1": {"parameters1": "value1"}}]
# """.strip()

OUTPUT_FORMAT_PROMPT = """
Write a pseudo-code for the job as a list of actions, so bots
could understand you. Never answer with a plain text.

Format:

[{"action_1": {"parameters1": "value1"}}]
""".strip()

FINISH_CHECK_PROMPT = "Check if job is finished. If OK, say 'finish_job'."

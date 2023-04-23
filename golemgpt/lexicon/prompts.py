from json import dumps as json_dumps


INSTRUCTIONAL_PROMPT = """
Write a pseudo-code defining a list of actions to execute, so bots could
understand that. You provide a list of actions, bots will execute them
and you will get results.

Bypass already executed actions, use results provided.
""".strip()

INITIALIZER_REPLY_EXAMPLE = json_dumps([
    {'ask_human_input': {'query': 'What is the goal?'}},
]).strip()

# - create_python_script: name, description, in_files, out_files
# - create_shell_script: name, description, in_files, out_files
# - delegate_job: goal, role, in_files, out_files

KNOWN_ACTIONS_PROMT = """
You can use the following actions, higher in the list means
the higher priority:

- get_os_details:
- get_local_date:
- read_file: filename, summazie_hint
- write_file: filename, content
- http_download: url, method, headers, body, out_filename
- run_script: name
- ask_human_input: query
- ask_google: query, out_filename
- explain: comment
- reject_job: message
- finish_job: message

Always find a corresponding actions from the list above.
""".strip()

KNOWN_ROLES_PROMT = ""

# KNOWN_ROLES_PROMT = """
# When using a the "delegate_job" action, assume the following roles:

# - "coder" can create function with defined goal, inputs and outputs
# - "admin" can install software on current machine
# """.strip()

# - "devops" can create configuration files for deployment
# - "webdesigner" can create HTML page and save it to the file
# - "artist" can create image and save it to the file
# - "reviewer" can review the code or action and provide feedback

OUTPUT_FORMAT_PROMPT = """
Always use machine readable JSON for every response. Don't add preambles.
Don't be verbose. Use the "explain" action to add thoughts, thanks, etc.

Format:

[
{"action_1": {"param_1": "value_1"}},
{"write_file": {"filename": "hello.txt", "content": "Hello there."}}
]
""".strip()

CHECK_COMPLETION_PROMPT = """
Check if job is completed after each action and respond with "finish_job"
on success.
""".strip()

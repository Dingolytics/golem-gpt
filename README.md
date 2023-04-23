Golem-GPT 
=========

![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dingolytics/golem-gpt?sort=date)

⚠️ **This is an experimental development. Run it on your own risk!** ⚠️

Framework for building actionable agents to achieve goals specified
by user, powered by [OpenAI](https://openai.com) [GPT-4](https://openai.com/research/gpt-4)
and [GPT-3.5](https://platform.openai.com/docs/models/gpt-3-5)


Usage
-----

The optimal way to run Golem-GPT is to use the [Docker image](https://hub.docker.com/r/dingolytics/golem-gpt) or Docker Compose.

### Requirements

- Docker or Python 3.8+ environment
- OpenAI API key

### Quick start

Put credentials to `.env`:

```bash
OPENAI_API_KEY=...
OPENAI_ORG_ID=...
OPENAI_MODEL=gpt-4
```

*(For `gpt-4` model you should have an early access enabled, it's not publicly available yet).*

Run it:

```bash
docker compose build && docker compose run app
```

It's also better to run it inside Docker to have it isolated. Because
Golem can access an environment and filesystem, so it's better to keep
it inside a container.


Architecture
------------

We introduce a novel framework for building **Golems** (actionable agents)
which is based on the following high-level concepts:

- **Goals**: a set of goals, initially defined by user's input. Goals could
  be high-level definitions, like "I want to build a web app", or low-level
  definitions, like "I want to create a new file with content 'Hello, world!'"

- **Cognitron**: a language model, which interprets input text and produces an
  action plan, or other kind of structured output. It runs on top of OpenAI
  models, which could be potentially replaced with any other language model.

- **Lexicon**: a set of rules and dictionary to generate prompts for Cognitron
  and interpret its structured output.

- **Action plan**: a structured output of Cognitron, which is a set of
  actions to be executed for achieving goals.

- **Actions**: a predefined executables or functions, which can interact
  with the environment to achieve goals. Actions could also be recursive or
  delegate their execution to other Golems.

- **Memory**: a storage for the Golem's current state, which can also be
  saved and loaded to continue the job later.

- **Codex**: a built-in Golem's moderator, which is responsible for
  checking the agent's actions and preventing it from doing something
  unexpected. Codex has its own Cognitrion and Lexicon.

NOTE: *In our implementation, Actions are implemented as Python functions*


Why?
----

**How is it different from [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT)?**

We build it because we like it. Our implementation is not as advanced
as AutoGPT to the moment, but it has some unique focus:

- Keeping it simple and easy to modify, also with minimal dependencies
- While keeping the core simple, we aim to make it extensible via custom
  actions, roles, policies, and other components
- We think of it as interactive tool, not necessarily to be fully autonomous
- Also we test it with GPT-3.5, which porbably sounds not super-hyped,
  but it's waaay cheaper and delivers results good enough for many use cases
- We are going to utilize it in our own development cycle, and refine it
  to fit real needs in software development


Actions supported
-----------------

The pipeline consists of the following actions:

- [x] ask_human_input(query)
- [x] get_os_details()
- [x] get_local_date()
- [x] read_file(filename)
- [x] write_file(filename, content)
- [ ] summarize_file(filename, hint, to_filename)
- [x] http_download(url, method, headers, body, to_filename)
- [ ] create_python_script(name, description, in_files, out_files)
- [ ] create_shell_script(name, description, in_files, out_files)
- [x] run_script(name)
- [ ] ask_google(query, to_filename)
- [ ] delegate_job(goal, role, in_files, out_files)
- [x] explain(comment)
- [x] reject_job(message)
- [x] finish_job(message)


Development
-----------

Setup virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip pip-tools
pip-compile
pip install -r requirements.txt
```

Put variables to `.env`:

```bash
OPENAI_API_KEY=...
OPENAI_ORG_ID=...
```

Start a new job:

```bash
python -m golemgpt
```

Continue saved job:

```bash
python -m golemgpt -j <job key>
```

Terminate simply with ^C or empty input.


License
-------

Golem-GPT is licensed under the [Apache-2.0](LICENSE).

Authors:

- Alexey Kinev <rudy@05bit.com>

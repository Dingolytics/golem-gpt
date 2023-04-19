GPT Golem
=========

Golem powered by OpenAI GPT.


Installation
------------

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


Usage
-----

Start a new job:

```bash
python -m gptgolem
```

Continue saved job:

```bash
python -m gptgolem -j <job key>
```

Terminate simply with ^C or empty input.

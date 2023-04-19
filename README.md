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

Start a new chat:

```bash
python -m chat
```

Continue saved chat:

```bash
python -m chat -k <chat key>
```

Terminate chat simply with ^C or empty input.

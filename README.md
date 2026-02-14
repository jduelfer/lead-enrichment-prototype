# Lead Enrichment Prototype
This prototype uses Google's Gemini API to ingest and enrich sample lead data.

## Install Instructions
These instructions have only been validated on WSL for Linux Ubuntu 20.04.6 LTS and assume python3.9 is installed (and assume `python3.9` is the current alias). Please adapt the installation instructions to your own system as applicable:

1. Create a virtual environment: `python3.9 -m venv .venv`
2. Activate virtual environment: `source .venv/bin/activate`
3. Install [Google GenAI SDK](https://ai.google.dev/gemini-api/docs/quickstart): `pip3.9 install -q -U google-genai`
4. Install [Pydantic](https://docs.pydantic.dev/latest/#why-use-pydantic): `pip3.9 install pydantic`
5. Deactivate the virtualenv: `deactivate`. We're going to set some env variables.
6. Within `.venv/bin/activate`, add the following lines (to the bottom is easiest):
    ```bash
    export PYTHONWARNINGS="ignore" # supresses warnings around python3.9 set up on the computer I perfomed the challenge on
    export GEMINI_API_KEY=<api_key> # <api_key> will be supplied separately and must be replaced
    ```
7. Reactivate the virtualenv: `source .venv/bin/activate`
8. Test installation by running `python3.9 test.py`. You should get a nice poem to think about.

## Usage Instructions
From the root of the project, simply run the following to use all defaults:
```bash
python3.9 main.py
```
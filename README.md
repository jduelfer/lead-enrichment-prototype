# Lead Enrichment Prototype
This prototype uses Google's Gemini API to ingest and enrich sample lead data. Furthermore, it uses [Structured Outputs](https://ai.google.dev/gemini-api/docs/structured-output?example=recipe) model capability to "ensure predicatable, type-safe results and simplifies extracting structured data from unstructured text." A scoring system is implemented to quickly score, rank, and filter leads based upon a set of criteria. 

## Before you begin
- You'll need a [Gemini API Key](https://aistudio.google.com/app/apikey) availble through Google's AI Studio. You can generate one for free and execute the script a couple times before hitting limits.
- Ensure at least Python 3.9+ is installed (required by the [google-genai python library](https://pypi.org/project/google-genai/)).
    - Helpful instructions if using WSL (Windows Subsystem for Linux): https://learn.microsoft.com/en-us/windows/python/web-frameworks

## Install Instructions
These instructions have been validated on the following systems:
- Ubuntu 22.05.5 LTS with Python 3.10
- Ubuntu 20.04.6 LTS with Python 3.9 (_EOL - not recommended_)

Please adapt the installation and usage instructions to your own system and aliases as applicable (your default python version may have a different alias than `python3`, so change as applicable):

1. Create a virtual environment: `python3 -m venv .venv`
2. Activate virtual environment: `source .venv/bin/activate`
3. Install [Google GenAI SDK](https://ai.google.dev/gemini-api/docs/quickstart): `pip3 install -q -U google-genai`
4. Install [Pydantic](https://docs.pydantic.dev/latest/#why-use-pydantic): `pip3 install pydantic`
5. Deactivate the virtualenv: `deactivate`. We're going to set some env variables.
6. Within `.venv/bin/activate`, add the following lines (to the bottom is easiest):
    ```bash
    export PYTHONWARNINGS="ignore" # supresses warnings around python3 set up on the computer I perfomed the challenge on
    export GEMINI_API_KEY=<api_key> # <api_key> will be supplied separately and must be replaced
    ```
7. Reactivate the virtualenv: `source .venv/bin/activate`
8. Test installation by running `python3 haiku.py`. You should get a nice poem to think about.

## Usage Instructions
From the root of the project, simply run:
```bash
python3 main.py
```

## Timebox and Next Steps
Given the time-box of 3-4 hours, my focus was on the core problem of enriching lead data via an LLM and validating an initial prototype. Future "backend dev" tasks to professionalize this agent would be:
1. Support command line arguments for the following:
    - `file`: easily load alternative data sets by specifying a path
    - `prompts`: support customization of prompts 
2. Improved scoring data models to better support configuration:
    - first step would be key/value dicts, such as `industry => score`
    - next step would be to load all scoring as its own model, such as an easily editable JSON file or similar.
3. Abstract _all_ configuration into a loadable object that would easily support an "Admin Portal" that could allow the Agent to be updated without pushing code and by super users.
4. For invalid leads (whether malformed JSON or failed responses during enrichment) prompt the user to manually evaluate and fix (prompt inputs, for example),
    - Futher down the line, these could be stored for review in the "Admin Portal" asynchronously.
5. Code cleanup:
    - Remove print statements - implement logging
    - Further elaborate on types and validations
    - Better exception handling via types of errors 

_Reminder to please consider this an initial prototype to evaluate solution design and technical approach limited to a few hours of development._ Python is also not my principal programming language, so please excuse the lack of best practices and common code conventions.
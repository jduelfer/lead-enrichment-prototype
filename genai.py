from google import genai
from pydantic import BaseModel, validate_call

LLM_MODEL = "gemini-3-flash-preview"

client = genai.Client()

@validate_call
def prompt_gemini(prompt: str, data_model):
    """
    Abstracts Gemini prompt into reusable and modular function. Alternative
    LLMs could be loaded and used to replace Gemini as desired.
    TODO: validate data_model param adheres to core BaseModel
    """
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": data_model.model_json_schema(),
        },  
    )
    return data_model.model_validate_json(response.text)
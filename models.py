import json
from google import genai
from pydantic import BaseModel, PositiveInt
from typing import Optional

HIGH_VALUE_INDUSTRIES = ["Cybersecurity", "AI"]
VALUABLE_INDUSTRIES = ["Fintech"]
SALES_SCORE_THRESHOLD = 70
MARKETING_ROUTE = "marketing_route"
PRIORITY_SALES_ROUTE = "PRIORITY_sales_route"
LLM_MODEL = "gemini-3-flash-preview"

client = genai.Client()

class RawLead(BaseModel):
    id: str
    email: str
    raw_note: str

class EnrichedData(BaseModel):
    industry: Optional[str]
    size: Optional[PositiveInt]
    intent: Optional[str]

class MeaningfulIntent(BaseModel):
    is_meaningful: bool
    reasoning: Optional[str]

class EnrichedLead(BaseModel):
    id: str
    email: str
    enriched_data: Optional[EnrichedData] = None
    score: int = 0
    crm_action: Optional[str] = MARKETING_ROUTE

    def enrich_data(self, raw_note: str, prompt: str, assumptions: str):
        """
        Takes the raw, free-form text from the Lead's web form submission and
        uses an LLM model to pull out enriched data. Uses Gemini's Structured
        Outputs for data extraction and structured classification.
        
        :param raw_note: free-form text input submitted by lead
        :type raw_note: str
        """
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt + raw_note + assumptions,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": EnrichedData.model_json_schema(),
            },  
        )
        self.enriched_data = EnrichedData.model_validate_json(response.text)

    def __determine_industry_value(self):
        """
        Increments score based upon the Lead's extracted industry (sector)
        TODO improve by establishing a dictionary with key/values
        """
        if self.enriched_data.industry in HIGH_VALUE_INDUSTRIES:
            self.score += 50
        elif self.enriched_data.industry in VALUABLE_INDUSTRIES:
            self.score += 25

    def __determine_size_fit(self):
        """
        Increments score if the extracted company size
        TODO thresholds could be integer keys with scores as values
        """
        if self.enriched_data.size > 100:
            self.score += 25
        elif self.enriched_data.size > 10:
            self.score += 10

    def calculate_score(self):
        if self.enriched_data != None:
            self.__determine_industry_value()
            self.__determine_size_fit()

    def determine_crm_action(self):
        """
        Assumes all leads are assigned to marketing unless threshold is surpassed
        """
        if self.score > SALES_SCORE_THRESHOLD:
            self.crm_action = PRIORITY_SALES_ROUTE

    def eval_meaningful_intent(self, prompt):
        """
        Attempts to piggy-back on previous intent extraction by validating that the
        captured intent seems meaninful (and therefor incrementing the lead score).
        Reasoning is captured/printed to help users debug.
        """
        if self.enriched_data.intent != None:
            response = client.models.generate_content(
                model=LLM_MODEL,
                contents=prompt + self.enriched_data.intent, # could alternatively be the raw note
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": MeaningfulIntent.model_json_schema(),
                },  
            )
            intent = MeaningfulIntent.model_validate_json(response.text)
            if (intent.is_meaningful):
                self.score += 10
                print("Intent detected: " + intent.reasoning)
            else:
                print("No intent detected for this lead: " + intent.reasoning)

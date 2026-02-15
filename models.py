from google import genai
from pydantic import BaseModel, PositiveInt
from typing import Optional

HIGH_VALUE_INDUSTRIES = ["Cybersecurity", "AI"]
VALUABLE_INDUSTRIES = ["Fintech"]
SALES_SCORE_THRESHOLD = 70
MARKETING_ROUTE = "marketing_route"
PRIORITY_SALES_ROUTE = "PRIORITY_sales_route"

client = genai.Client()

class RawLead(BaseModel):
    id: str
    email: str
    raw_note: str

class EnrichedData(BaseModel):
    industry: Optional[str]
    size: Optional[PositiveInt]
    intent: Optional[str]

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
            model="gemini-3-flash-preview",
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
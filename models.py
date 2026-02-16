from pydantic import BaseModel, PositiveInt
from genai import prompt_gemini
from typing import Optional

HIGH_VALUE_INDUSTRIES = ["Cybersecurity", "AI"]
VALUABLE_INDUSTRIES = ["Fintech"]
SALES_SCORE_THRESHOLD = 70
MARKETING_ROUTE = "marketing_route"
PRIORITY_SALES_ROUTE = "PRIORITY_sales_route"
LLM_MODEL = "gemini-3-flash-preview"

class Config(BaseModel):
    enrichmentPrompt: str
    enrichmentAssumptions: str
    meaningfulIntentPrompt: str

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
        self.enriched_data = prompt_gemini(prompt + raw_note + assumptions, EnrichedData)

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
        if self.enriched_data.size != None:
            if self.enriched_data.size > 100:
                self.score += 25
            elif self.enriched_data.size >= 10:
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
        captured intent seems meaningful (and therefor incrementing the lead score).
        Reasoning is stored for debugging in future cases.
        """
        if self.enriched_data.intent != None:
            # could alternatively pass in the raw_note instead of already processed intent
            intent = prompt_gemini(prompt + self.enriched_data.intent, MeaningfulIntent)
            if (intent.is_meaningful):
                self.score += 10

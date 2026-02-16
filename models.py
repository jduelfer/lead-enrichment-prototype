from pydantic import BaseModel, PositiveInt, validate_call
from genai import prompt_gemini
from typing import Optional

MARKETING_ROUTE = "marketing_route"

class Config(BaseModel):
    enrichment_prompt: str
    enrichment_assumptions: str
    industry_score: dict[str, int]
    llm: str
    meaningful_intent_prompt: str
    meaningful_intent_score: int
    priority_sales_route: str
    priority_sales_threshold: int

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
    crm_action: str = MARKETING_ROUTE

    def enrich_data(self, llm: str, prompt: str):
        """
        Takes the raw, free-form text from the Lead's web form submission and
        uses an LLM model to pull out enriched data. Uses Gemini's Structured
        Outputs for data extraction and structured classification.
        """
        self.enriched_data = prompt_gemini(llm, prompt, EnrichedData)

    @validate_call
    def __determine_industry_value(self, config: Config):
        """
        Increments score based upon the Lead's extracted industry (sector)
        """
        if self.enriched_data.industry != None and self.enriched_data.industry in config.industry_score:
            self.score += config.industry_score[self.enriched_data.industry]

    def __determine_size_fit(self):
        """
        Increments score if the extracted company size is within the applicable threshold.
        TODO thresholds could be integer keys with scores as values
        """
        if self.enriched_data.size != None:
            if self.enriched_data.size > 100:
                self.score += 25
            elif self.enriched_data.size >= 10:
                self.score += 10

    @validate_call
    def calculate_score(self, config: Config):
        if self.enriched_data != None:
            self.__determine_industry_value(config)
            self.__determine_size_fit()

    @validate_call
    def determine_crm_action(self, config: Config):
        """
        Assumes all leads are assigned to default unless threshold is surpassed
        """
        if self.score > config.priority_sales_threshold:
            self.crm_action = config.priority_sales_route

    @validate_call
    def eval_meaningful_intent(self, config: Config):
        """
        Attempts to piggy-back on previous intent extraction by validating that the
        captured intent seems meaningful (and therefor incrementing the lead score).
        Reasoning is stored for debugging in future cases.
        """
        if self.enriched_data.intent != None:
            # could alternatively pass in the raw_note instead of already processed intent
            intent = prompt_gemini(config.llm, config.meaningful_intent_prompt + self.enriched_data.intent, MeaningfulIntent)
            if (intent.is_meaningful):
                self.score += config.meaningful_intent_score

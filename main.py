import json
import pprint
from pydantic import ValidationError, validate_call
from models import Config, RawLead, EnrichedLead

@validate_call
def load(filename: str):
    """
    Loads local files for data and configuration. Avoids custom exception handling to
    take advantage of python interpreter for malformed JSON files.
    """
    with open(filename, 'r') as file:
        return json.load(file)

@validate_call    
def ingest(lead_data: list[dict]):
    """
    Ingests raw, unvalidated web form data and ensures it adheres to pydantic spec. Stores
    and returns invalid leads (malformed or unexpected JSON) for manual review.
    """
    raw_leads, invalid_leads = [], []
    for lead in lead_data:
        try:
            raw_leads.append(RawLead(**lead))
        except ValidationError as e:
            invalid_leads.append(lead)
    return raw_leads, invalid_leads

@validate_call
def enrich(config: Config, raw_lead: RawLead):
    """
    Enriches a web-form lead by combining LLM output and scoring data
    to determine if a lead fits an Ideal Customer Profile. Stores any exception
    during enrichment for futher review.
    """
    enriched_lead = EnrichedLead(id=raw_lead.id, email=raw_lead.email)
    lead_exception = None
    try:
        prompt = config.enrichment_prompt + raw_lead.raw_note + config.enrichment_assumptions 
        enriched_lead.enrich_data(config.llm, prompt)
    except Exception as e:
        lead_exception = e

    if enriched_lead.enriched_data != None:
        enriched_lead.calculate_score(config)
        enriched_lead.determine_crm_action(config)
        try:
            enriched_lead.eval_meaningful_intent(config)
        except Exception as e:
            lead_exception = e
    return enriched_lead, lead_exception
    
def run():
    config = Config(**load('config.json'))
    lead_data = load('leads.json')
    raw_leads, invalid_leads = ingest(lead_data)

    enriched_leads, requiring_review = [], []
    for raw_lead in raw_leads:
        print("Enriching lead " + raw_lead.id)
        enriched_lead, lead_exception = enrich(config, raw_lead)
        if lead_exception != None:
            print("Issue encountered enriching lead with id " + raw_lead.id)
            print(lead_exception)
            requiring_review.append(enriched_lead) 
        else:
            enriched_leads.append(enriched_lead)

    return [enriched_lead.model_dump(mode='json') for enriched_lead in enriched_leads] 

crm_data = run()
pprint.pp(crm_data)
json_export = json.dumps(crm_data)
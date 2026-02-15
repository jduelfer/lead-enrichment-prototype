import json
import pprint
from pydantic import ValidationError, validate_call
from models import RawLead, EnrichedLead

ENRICHMENT_PROMPT = "Determine the Industry of the company, Size of the company in number of employees, and the Lead's intent based upon the following description submitted by the Lead: "
ENRICHMENT_ASSUMPTIONS = " Assume the size of the company is greater than 0."
MEANINGFUL_INTENT_PROMPT = "Determine if the following Lead has meaningful intent. Look for helpful keywords, like need, interested, looking, or verbs indicating what is needed : "

def load():
    """
    Loads a local file accessible via the project.
    Avoids exception handling to use default error messages, which are helpful
    for debugging malformed JSON.
    TODO update to configurable param. 
    """
    with open('leads.json', 'r') as file:
        return json.load(file)
    
def ingest(lead_data):
    """
    Ingests raw, unvalidated web form data and ensures
    it adheres to the spec. Stores invalid lead data for
    potential manual processing.
    
    :param lead_data: Unvalidated web form submissions as a serialized JSON string
    :type lead_data: str
    """
    raw_leads = []
    invalid_leads = [] # can be manually reviewed later on

    for lead in lead_data:
        try:
            raw_leads.append(RawLead(**lead))
        except ValidationError as e:
            invalid_leads.append(lead)
    return raw_leads, invalid_leads

@validate_call
def enrich(raw_lead: RawLead):
    """
    Enriches a web-form lead by combining LLM output and scoring data
    to determine if a lead fits an Ideal Customer Profile.
    
    :param raw_lead: web-form submitted lead
    :type raw_lead: RawLead
    """
    enriched_lead = EnrichedLead(id=raw_lead.id, email=raw_lead.email)
    print("Enriching Lead Data for " + enriched_lead.id + "...")
    enriched_lead.enrich_data(raw_lead.raw_note, ENRICHMENT_PROMPT, ENRICHMENT_ASSUMPTIONS)
    enriched_lead.calculate_score()
    enriched_lead.determine_crm_action()
    print("Evaluating Meaningful Intent...")
    enriched_lead.eval_meaningful_intent(MEANINGFUL_INTENT_PROMPT)
    return enriched_lead
    
def run():
    lead_data = load()
    raw_leads, invalid_leads = ingest(lead_data)

    # Current status
    print("Leads correctly ingested for enrichment: " + str(len(raw_leads)) + " of " + str(len(lead_data)))
    print("Invalid leads for manual review: " + str(len(invalid_leads)))
    # TODO: with extra time, we could prompt the user to review and "fix" any
    # pieces of invalid data before continuing onto enrichment.

    # TODO: expand to list - single lead for testing
    enriched_lead = enrich(raw_leads[0])
    pprint.pp(enriched_lead.model_dump(mode='json'))

run()
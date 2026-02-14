import json
from google import genai
from pydantic import ValidationError, validate_call
from lead import RawLead, EnrichedData, EnrichedLead

# variable for easily editing
prompt = "Determine the Industry of the company, Size of the company in number of employees, and the Lead's intent based upon the following description submitted by the Lead: "
assumptions = " Assume the size of the company is greater than 0."

def load():
    """
    TODO update to configurable param
    """
    with open('leads.json', 'r') as file:
        return json.load(file)
    
def ingest(lead_data):
    """
    Ingests raw, unvalidated web form data and ensures
    it adheres to the spec.
    
    :param lead_data: Unvalidated web form submissions in JSON format
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
def enrich_data(raw_note: str):
    """
    Takes the raw, free-form text from the Lead's web form submission and
    uses an LLM model to pull out enriched data. Uses Gemini's Structured
    Outputs for data extraction and structured classification.
    
    :param raw_note: free-form text input submitted by lead
    :type raw_note: str
    """
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt + raw_note + assumptions,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": EnrichedData.model_json_schema(),
        },  
    )
    return EnrichedData.model_validate_json(response.text)

@validate_call
def enrich(raw_lead: RawLead):
    """
    Docstring for enrich
    
    :param raw_lead: Description
    :type raw_lead: RawLead
    """
    enriched_lead = EnrichedLead(id=raw_lead.id, email=raw_lead.email)
    enriched_lead.enriched_data = enrich_data(raw_lead.raw_note)
    enriched_lead.calculate_score()
    enriched_lead.determine_crm_action()
    return enriched_lead
    
def run():
    lead_data = load() # lets python highlight any issues wihtin the JSON
    raw_leads, invalid_leads = ingest(lead_data)

    # Current status
    print("Leads ingested: " + str(len(raw_leads)) + " of " + str(len(lead_data)))
    print("Invalid leads for manual review: " + str(len(invalid_leads)))

    # TODO: expand to list - single lead for testing
    enriched_lead = enrich(raw_leads[0])

    print(enriched_lead)

run()
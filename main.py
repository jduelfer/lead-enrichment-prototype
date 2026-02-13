import json
from google import genai
from pydantic import ValidationError
from lead import RawLead

# can restructure to replace with command line arg instead of hard coded
try:
    with open('leads.json', 'r') as file:
        lead_data = json.load(file)
except:
    print("Error: lead data could not be loaded.")

raw_leads = []
invalid_leads = [] # can be manually reviewed later on

for lead in lead_data:
    try:
        raw_leads.append(RawLead(**lead))
    except ValidationError as e:
        invalid_leads.append(lead)

client = genai.Client()

# prototype
print("Enriched leads: " + str(len(leads)) + " of " + str(len(raw_leads)))
print("Invalid leads for manual review: " + str(len(invalid_leads)))
import os
base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
params = {"size": "39", "apikey": os.getenv('ticketmaster'), "city": "{city}", "stateCode": "{stateCode}"}

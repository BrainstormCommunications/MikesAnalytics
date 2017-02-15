from support.api_config import config
import os
import json
import psycopg2
from psycopg2.extras import Json

data_directory = config["data_directory"]
event_filename = config["event_filename"]
app_location = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
event_data_src = os.path.join(app_location, data_directory, event_filename)
with open(event_data_src, encoding='ascii', errors='ignore') as data_file:
    event_data = json.load(data_file)

analytics_db_name = config["DATABASE_NAME"]
analytics_connect = psycopg2.connect(database=analytics_db_name)
litt = 0
for mixpanel_event in event_data:
    for key in mixpanel_event["properties"].keys():
        if "$" in key:
            mixpanel_event["properties"][key.replace("$", "")] = mixpanel_event["properties"].pop(key)
    cur = analytics_connect.cursor()
    cur.execute(
        "INSERT INTO mixpanel_event (content_data) VALUES (%s)",
        [Json(mixpanel_event)])
    analytics_connect.commit()
    litt += 1
    print(litt)

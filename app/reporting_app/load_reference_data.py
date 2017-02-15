from support.api_config import config
import os
import json
import psycopg2
from psycopg2.extras import Json

data_directory = config["data_directory"]
event_filename = config["event_filename"]
app_location = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
event_data_src = os.path.join(app_location, data_directory, event_filename)

with open(event_data_src) as data_file:
    event_data = json.load(data_file)

model_file_prefix = config["MODEL_FILE_PREFIX"]
name_parts_dict = config["NAME_PARTS"]
analytics_db_name = config["DATABASE_NAME"]
analytics_connect = psycopg2.connect(database=analytics_db_name)

for asset_type, lookup_values in name_parts_dict.items():
    asset_filename = "%s%s.json" % (
        model_file_prefix, lookup_values["file_name"])
    asset_src = event_data_src = os.path.join(
        app_location, data_directory, asset_filename)
    with open(asset_src, encoding='utf-8') as data_file:
        event_data = json.load(data_file)
    this_event_schema = list(event_data[0].keys())
    insert_data = "'),('".join(str(x) for x in event_data)
    insert_statement = """
        INSERT INTO app_%s (content_data) VALUES
         """ % (lookup_values["table_name"],)
    cur = analytics_connect.cursor()
    for data_record in event_data:
        cur.execute(insert_statement + "(%s)", [Json(data_record)])
        analytics_connect.commit()

from support.api_config import config
from support import sql_reporting as sql
import os
import psycopg2

# I can't find another way to reliably find the directory parents etc.
app_location = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
app_location = os.path.split(app_location)[0]
# This points us back up to secrets.xml, an xml with keys, secrets and other
# private config options that cannot be made public
settings_dict = {
    "REPORTING_DESTINATION": os.path.join(app_location, "reporting_exports",""),
}

analytics_db_name = config["DATABASE_NAME"]
analytics_connect = psycopg2.connect(database=analytics_db_name)
cur = analytics_connect.cursor()
SQL_QUERIES = [
    sql.CORE_REPORT_SQL,
    sql.EVENT_OVERVIEW_SQL,
    sql.MEDIA_INTERACTION_SQL,
]

for query in SQL_QUERIES:
    cur.execute(query.format(**settings_dict))

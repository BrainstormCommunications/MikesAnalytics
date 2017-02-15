from support.api_config import config
import support.mx_event_export as mx
import os
import json
from datetime import date
from datetime import timedelta
from datetime import strftime
d.strftime("%Y")

data_directory = config["data_directory"]
event_filename = config["event_filename"]
api_secret = config["MIXPANEL_SECRET"]
methods = ["export"]
YESTERDAY = date.today() - timedelta(days = 1)
YESTERDAY = YESTERDAY.strftime("%Y-%m-%d")
params = {"from_date": "2017-01-01", "to_date": YESTERDAY}
app_location = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
data_destination = os.path.join(app_location, data_directory, event_filename)

mixpanel_report = mx.Mixpanel(api_secret)
output = mixpanel_report.request(methods=methods, params=params)
with open(data_destination, 'w') as outfile:
    json.dump(output, outfile)

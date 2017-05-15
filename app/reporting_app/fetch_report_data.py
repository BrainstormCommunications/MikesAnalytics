from support.api_config import config
import support.mx_event_export as mx
import os
import json
from datetime import date
from datetime import timedelta
from datetime import datetime

data_directory = config["data_directory"]
event_filename = config["event_filename"]
api_secret = config["MIXPANEL_SECRET"]
methods = ["export"]
app_location = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
data_destination = os.path.join(
    app_location,
    data_directory,
    "byday"
)

report_date = datetime.strptime("2017-01-29", "%Y-%m-%d").date()
while report_date < date.today():
    report_date_fmt = datetime.strftime(report_date, "%Y-%m-%d")
    params = {"from_date": report_date_fmt, "to_date": report_date_fmt}
    print(report_date_fmt)
    mixpanel_report = mx.Mixpanel(api_secret)
    datafile = os.path.join(
        data_destination,
        "{}.json".format(report_date_fmt)
    )
    output = mixpanel_report.request(methods=methods, params=params)
    with open(datafile, 'w') as outfile:
        json.dump(output, outfile)
    report_date = report_date + timedelta(days=1)

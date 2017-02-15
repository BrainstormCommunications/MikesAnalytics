import os
import xmltodict

# I can't find another way to reliably find the directory parents etc.
app_location = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
app_location = os.path.split(app_location)[0]
app_location = os.path.split(app_location)[0]
# This points us back up to secrets.xml, an xml with keys, secrets and other
# private config options that cannot be made public
data_source = os.path.join(app_location, "settings", "secrets.xml")
with open(data_source, "rb") as secrets_xml:
    secrets_import = xmltodict.parse(secrets_xml, process_namespaces=True)
# This just creates a config dictionary that we can use across the needed
config = {
    "MIXPANEL_TOKEN": secrets_import["SECRETS"]["MIXPANEL_TOKEN"],
    "MIXPANEL_SECRET": secrets_import["SECRETS"]["MIXPANEL_SECRET"],
    "DATABASE_NAME": "JLR_Analytics",
    "MODEL_FILE_PREFIX": "IModel",
    "NAME_PARTS": {
        "asset": {"table_name": "asset", "file_name": "Asset"},
        "folio": {"table_name": "folio", "file_name": "Folio"},
        "folioitem": {"table_name": "folioitem", "file_name": "FolioItem"},
        "foliosubject": {
            "table_name": "foliosubject",
            "file_name": "FolioSubject"
        },
        "foliotopic": {"table_name": "foliotopic", "file_name": "FolioTopic"},
        "infocard": {"table_name": "infocard", "file_name": "InfoCard"},
    },
    "data_directory": "datasrc",
    "event_filename": "all_event_dump.json"
}

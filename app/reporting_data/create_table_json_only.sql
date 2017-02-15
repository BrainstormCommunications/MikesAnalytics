CREATE TABLE app_asset (
   id bigserial PRIMARY KEY,
   content_data json
);

CREATE TABLE app_folio (
   id bigserial PRIMARY KEY,
   content_data json
);

CREATE TABLE app_infocard (
   id bigserial PRIMARY KEY,
   content_data json
);

CREATE TABLE app_foliotopic (
   id bigserial PRIMARY KEY,
   content_data json
);

CREATE TABLE app_foliosubject (
   id bigserial PRIMARY KEY,
   content_data json
);

CREATE TABLE app_folioitem (
   id bigserial PRIMARY KEY,
   content_data json
);

CREATE TABLE mixpanel_event (
   id bigserial PRIMARY KEY,
   content_data json
);
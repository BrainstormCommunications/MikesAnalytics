CORE_REPORT_SQL = """
COPY(
/*
This is the core report query that gives the day range figures over a series of
days. The awkward -> an ->> operators relate to the JSON querying in Postgres
as I have used everything in documents to help ease of storing and use.

In all cases we filter out the cookie created distinct ids 
*/
-- Start with the WITH statement to provide sub selects
WITH 
-- Create the full date series
    full_dates AS (
        select generate_series(0,180) + date '1/1/2017' as fulldate
    ),

-- Create table for user-oriented aggregations
-- By day it gives the number of users whose first session was that day
    first_user_sessions AS (
        WITH first_sessions AS (
            -- And it does so with this sub select which provides the earliest
            -- date a user is seen
            SELECT 
                me.content_data -> 'properties' ->> 'distinct_id' AS distinct_id,
                to_timestamp(MIN(CAST(me.content_data -> 'properties' ->> 'time' AS integer))) AS first_date
            FROM 
                public.mixpanel_event me  
            WHERE 
                me.content_data ->> 'event' = 'Session'
                AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
            GROUP BY 1
            )
        
        SELECT 
            date(first_date) AS this_date,
            COUNT(*) AS number_inducted 
        FROM first_sessions
        GROUP BY 1
    ),

-- Create the table for session-oriented aggregations
-- By day it gives the total number of sessions and the total time spent in minutes
    overall_sessions AS (
        SELECT
            date(to_timestamp(CAST(me.content_data -> 'properties' ->> 'time' AS integer))) AS this_date,
            COUNT(*) AS number_of_sessions,
            SUM(CAST(me.content_data -> 'properties' ->> 'duration' AS numeric))/60 AS total_time
        FROM 
            public.mixpanel_event me  
        WHERE 
            me.content_data ->> 'event' = 'Session'
            AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
        GROUP BY 1),

-- This sub select gives us the number of individual users on a given day by using the distinct id
    number_of_users AS (
        WITH pairings AS (
            -- By identifying distinct pairings of days and distinct_ids
            SELECT DISTINCT 
                date(to_timestamp(CAST(me.content_data -> 'properties' ->> 'time' AS integer))) AS this_date,
                me.content_data -> 'properties' ->> 'distinct_id' AS distinct_id 
            FROM 
                public.mixpanel_event me  
            WHERE 
                me.content_data ->> 'event' = 'Session'
                AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
        )   
        
        SELECT 
            this_date, 
            COUNT(*) AS distinct_users 
        FROM 
            pairings 
        GROUP BY 1),

-- This sub select treats folio downloads, folio shows, and folio item shows
-- Using FILTER syntax to do in line filterinf on aggregates for clarity
-- For some reason I'm having trouble getting quite the level of use from the 
-- FILTER as I'd like... might be owing to the joins
    video_watches AS (

        SELECT
            date(to_timestamp(CAST(me.content_data -> 'properties' ->> 'time' AS integer))) AS this_date,
            COUNT(*) FILTER (WHERE apa.content_data ->> 'brand' = 'LR') AS landrover_video_watch,
            COUNT(*) FILTER (WHERE apa.content_data ->> 'brand' = 'J') AS jaguar_video_watch
        FROM 
            public.mixpanel_event me
            JOIN app_asset apa ON  me.content_data -> 'properties' ->> 'AssetId' = apa.content_data ->> '_id'
        WHERE 
            me.content_data ->> 'event' = 'ShowAsset'
            AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
            AND apa.content_data ->> 'type' = 'VIDEO'
        GROUP BY 1
        ),

   folio_downloads AS (

        SELECT
            date(to_timestamp(CAST(me.content_data -> 'properties' ->> 'time' AS integer))) AS this_date,
            COUNT(*) FILTER (WHERE afod.content_data ->> 'brand' = 'LR') AS landrover_folio_download,
            COUNT(*) FILTER (WHERE afod.content_data ->> 'brand' = 'J') AS jaguar_folio_download

        FROM 
            public.mixpanel_event me
            JOIN app_folio afod ON me.content_data -> 'properties' ->> 'ID' = afod.content_data ->> '_id'
        
        WHERE 
            me.content_data ->> 'event' = 'FolioDownload'
            AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
        GROUP BY 1
        ),

    folio_shows AS (

        SELECT
            date(to_timestamp(CAST(me.content_data -> 'properties' ->> 'time' AS integer))) AS this_date,
            COUNT(*) FILTER (WHERE afos.content_data ->> 'brand' = 'LR') AS landrover_show_folio,
            COUNT(*) FILTER (WHERE  afos.content_data ->> 'brand' = 'J') AS jaguar_show_folio

        FROM 
            public.mixpanel_event me
            JOIN app_folio afos ON me.content_data -> 'properties' ->> 'FolioId' = afos.content_data ->> '_id'
        
        WHERE 
            me.content_data ->> 'event' = 'ShowFolio'
            AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
        GROUP BY 1
        )
-- Assemble all of the data into the report
SELECT 
    fulldate,
    COALESCE(number_inducted,0) AS number_inducted, 
    COALESCE(total_time,0) AS total_time_in_mins, 
    COALESCE(number_of_sessions,0) AS number_of_sessions,
    COALESCE(distinct_users,0) AS number_of_users,
    COALESCE(landrover_video_watch,0) AS landrover_video_watch,
    COALESCE(jaguar_video_watch,0) AS jaguar_video_watch,
    COALESCE(landrover_show_folio,0) AS landrover_show_folio,
    COALESCE(jaguar_show_folio,0) AS jaguar_show_folio,
    COALESCE(landrover_folio_download,0) AS landrover_folio_download,
    COALESCE(jaguar_folio_download,0) AS jaguar_folio_download

FROM 
    full_dates fd
    LEFT OUTER JOIN first_user_sessions fus ON fd.fulldate = fus.this_date
    LEFT OUTER JOIN overall_sessions ova ON fd.fulldate = ova.this_date
    LEFT OUTER JOIN number_of_users nou ON fd.fulldate = nou.this_date
    LEFT OUTER JOIN video_watches vw ON fd.fulldate = vw.this_date
    LEFT OUTER JOIN folio_downloads fod ON fd.fulldate = fod.this_date
    LEFT OUTER JOIN folio_shows fsh  ON fd.fulldate = fsh.this_date
ORDER BY 1 ASC)  TO '{REPORTING_DESTINATION}TopStats.csv' CSV DELIMITER ',' HEADER;
"""
EVENT_OVERVIEW_SQL = """
COPY(
WITH distinct_user_events AS (
    WITH user_pairings AS (
        SELECT DISTINCT 
            me.content_data ->> 'event' AS event_name,
            me.content_data -> 'properties' ->> 'distinct_id'
         FROM 
                public.mixpanel_event me
        WHERE me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%')

    SELECT event_name, COUNT(*) AS users FROM user_pairings GROUP BY 1)

SELECT 
    me.content_data ->> 'event' AS event_name,
    COUNT(*) AS number_of_events,
    due.users AS number_of_users
FROM
    public.mixpanel_event me
    JOIN distinct_user_events due ON me.content_data ->> 'event' = due.event_name
WHERE me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
GROUP BY 1,3)  TO '{REPORTING_DESTINATION}EventOverview.csv' CSV DELIMITER ',' HEADER;
"""

MEDIA_INTERACTION_SQL = """
COPY(
SELECT
    'Video' AS view_type,
    apa.content_data ->> 'title' AS title,
    CASE WHEN apa.content_data ->> 'brand' = 'LR' THEN 'Land Rover' ELSE 'Jaguar' END AS brand,
    COUNT(*) AS number_of_views
FROM 
    public.mixpanel_event me
    JOIN app_asset apa ON  me.content_data -> 'properties' ->> 'AssetId' = apa.content_data ->> '_id'
WHERE 
    me.content_data ->> 'event' = 'ShowAsset'
    AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
    AND apa.content_data ->> 'type' = 'VIDEO'
GROUP BY 1,2,3
UNION ALL
SELECT
    'Folio View' AS view_type,
    afo.content_data ->> 'title' AS title,
    CASE WHEN afo.content_data ->> 'brand' = 'LR' THEN 'Land Rover' ELSE 'Jaguar' END AS brand,
    COUNT(*) AS number_of_views
FROM 
    public.mixpanel_event me
    JOIN app_folio afo ON  me.content_data -> 'properties' ->> 'FolioId' = afo.content_data ->> '_id'
WHERE 
    me.content_data ->> 'event' = 'ShowFolio'
    AND me.content_data -> 'properties' ->> 'distinct_id' NOT LIKE '%%-%%'
GROUP BY 1,2,3
ORDER BY 1,4 DESC)  TO '{REPORTING_DESTINATION}MediaInteraction.csv' CSV DELIMITER ',' HEADER;
"""
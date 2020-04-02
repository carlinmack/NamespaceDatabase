SELECT 'How many:' AS '';

SELECT count(*) AS '- users:' 
FROM user;

SELECT count(*) AS '- pages:' 
FROM page;

SELECT count(*) AS '- edits:' 
FROM edit;
SELECT '' AS '';

SELECT '- partitions that are done vs error:' AS '';
SELECT status AS 'job status', count(id) AS 'count' FROM partition GROUP BY status;
SELECT '' AS ''; 
SELECT file_name, error from partition where error is not null; 

SELECT AVG(TIMESTAMPDIFF(SECOND,start_time_1,end_time_1)) AS 'Average time to parse dump (secs):' FROM partition WHERE status = 'done';

SELECT TIMESTAMPDIFF(Minute,Min(start_time_1),Max(end_time_1)) AS 'Total time parsing dumps (mins):' FROM partition WHERE status = 'done';

SELECT FORMAT(IF(population=0,0,target/population),2) AS 'Dumps per minute:' 
FROM (
    SELECT 
        (SELECT count(*) FROM partition where status = 'done') AS target,
        (SELECT TIMESTAMPDIFF(Minute,Min(start_time_1),Max(end_time_1)) FROM partition WHERE status = 'done') AS population
    ) AS proportion; 

SELECT 'Distribution of:' AS '';
SELECT '- users by number of mainspace edits:' AS '';
SELECT 
    (SELECT count(*) FROM user WHERE number_of_edits = 0) AS 'no edits', 
    (SELECT count(*) FROM user WHERE number_of_edits = 1) AS '1 edit', 
    (SELECT count(*) FROM user WHERE number_of_edits > 1 and number_of_edits <= 10) AS '2-10 edits', 
    (SELECT count(*) FROM user WHERE number_of_edits > 10 and number_of_edits <= 100) AS '11-100 edits', 
    (SELECT count(*) FROM user WHERE number_of_edits > 100) AS '>100 edits';
    
SELECT '- users by number of talkpage edits:' AS '';
SELECT 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 0) AS 'no edits', 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 1) AS '1 edit', 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10) AS '2-10 edits', 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100) AS '11-100 edits', 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 100) AS '>100 edits';
SELECT '- pages by namespace:' AS '';
SELECT namespace, count(page_id) AS 'count' FROM page GROUP BY namespace; 
SELECT '' AS '';

SELECT 'Size of database:' AS '';
SELECT table_schema AS "Database", SUM(data_length + index_length) / 1024 / 1024 / 1024 AS "Size (GB)" 
    FROM information_schema.TABLES GROUP BY table_schema;


SELECT 'Size of tables:' AS '';
SELECT 
    table_name AS 'Table', 
    round(((data_length + index_length) / 1024 / 1024 ), 2) `Size in MB` 
FROM information_schema.TABLES
WHERE table_name = "edit" or table_name = "page" or table_name = "user" or table_name = "partition";

SELECT 'users with most edits:' AS '';
SELECT username, number_of_edits AS 'mainspace edits' 
FROM user
where bot is null 
order by number_of_edits desc 
limit 5;

SELECT 'bots with most edits:' AS '';
SELECT username, number_of_edits AS 'mainspace edits' 
FROM user
where bot is True
order by number_of_edits desc 
limit 5;

SELECT 'users with most talkpage edits:' AS '';
SELECT username, talkpage_number_of_edits AS 'talkpage edits' 
FROM user 
where bot is null 
order by talkpage_number_of_edits desc limit 5;
SELECT '' AS '';

SELECT 'ip users with most reversions:' AS '';
SELECT ip_address, reverted_edits 
FROM user 
where ip_address is not null 
order by reverted_edits desc 
limit 5;

-- Connecting blocked users to edits
--      What do the blocked users edits look like?  (number words/chars, mostly adds, mostly deletes,...)
--          How does that compare to non-blocked users?
-- ASk general questions: list of users with the top 10% of edit length or bottom 10% of edit length, compare against blocked users?
--      Different ways to get “good” users or “bad” users (look for trends)
--          Look for trends
--          Compare with manual blocked users list
--      % (and users) of users whose additions are deleted
--          Did the users who had their (or all their, or x% of their) additions deleted end up being blocked?
--          Did the users who had their (or all their, or x% of their) changes reverted/undid end up being blocked?
-- Intersection of blocked users and talk-page users - only blocked users who also edited talk pages.
SELECT 'How many:' AS '';

SELECT count(*) AS '- users:' 
FROM user;

SELECT count(*) AS '- users with over 100 edits:' 
FROM user WHERE number_of_edits > 100;

SELECT count(*) AS '- pages:' 
FROM page;

SELECT count(*) AS '- edits:' 
FROM edit;
-- SELECT count(*) AS '- IP users that edit talkpages:' FROM edit;
SELECT '' AS '';

SELECT 'Proportion of:' AS '';
    /* - edits containing bad words */
    /* - ip users that edit talkpages */
SELECT CONCAT(FORMAT(IF(main=0,0,(talk*100.0)/main),2),'%') AS '- pages with talk pages:' FROM (SELECT (SELECT count(page_id) FROM page WHERE namespace =0) AS main,
(SELECT count(page_id) FROM page WHERE namespace = 1) AS talk) AS proportion; 
SELECT '- partitions that are done vs error:' AS '';
SELECT status AS 'job status', count(id) AS 'count' FROM partition GROUP BY status; 
SELECT '' AS '';

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

SELECT 'Size of databASe:' AS '';
SELECT table_schema AS "DatabASe", SUM(data_length + index_length) / 1024 / 1024 / 1024 AS "Size (GB)" 
    FROM information_schema.TABLES GROUP BY table_schema;

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
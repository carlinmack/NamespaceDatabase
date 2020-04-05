SELECT 'How many:' AS '';

SELECT count(*) AS '- users:'
FROM user;

SELECT count(*) AS '- pages:' 
FROM page;

SELECT count(*) AS '- edits:' 
FROM edit;
SELECT '' AS '';

SELECT count(*) INTO @numUsers
FROM user;

SELECT count(*) INTO @numIpUsers
FROM user
WHERE ip_address is not NULL;

SELECT count(*) INTO @numPages
FROM user;

SELECT count(*) INTO @numEdits
FROM edit;

SELECT 'Proportion of:' AS '';
-- IP users that edit talkpages
SELECT CONCAT(FORMAT(IF(@numIpUsers=0,0,(talk*100.0)/@numIpUsers),2),'%') AS '- IP users that edit talkpages:' 
FROM (
    SELECT count(*) as talk FROM user 
        WHERE ip_address is not NULL and talkpage_number_of_edits > 0) AS proportion; 

-- pages with talk pages:
SELECT CONCAT(FORMAT(IF(main=0,0,(talk*100.0)/main),2),'%') AS '- pages with talk pages:' 
FROM (
    SELECT 
        (SELECT count(page_id) FROM page WHERE namespace = 0) AS main,
        (SELECT count(page_id) FROM page WHERE namespace = 1) AS talk
    ) AS proportion; 

-- talkpage edits with profanity:
SELECT CONCAT(FORMAT(IF(@numEdits=0,0,(target*100.0)/@numEdits),2),'%') AS '- talkpage edits with profanity:' 
FROM (
    SELECT count(page_id) AS target FROM edit WHERE ins_vulgarity = 1) AS proportion; 
SELECT '' AS '';
-- edits mainspace and talkspace'
SELECT CONCAT(FORMAT(IF(@numUsers=0,0,(target*100.0)/@numUsers),2),'%') AS 'edits mainspace and talkspace' 
FROM (
    select count(*) as target from user 
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0) as p;

-- edits mainspace but not talkspace
SELECT CONCAT(FORMAT(IF(@numUsers=0,0,(target*100.0)/@numUsers),2),'%') 'edits mainspace but not talkspace' 
FROM (
    select count(*) as target from user 
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0) as p;

-- edits talkspace but not mainspace
SELECT CONCAT(FORMAT(IF(@numUsers=0,0,(target*100.0)/@numUsers),2),'%') 'edits talkspace but not mainspace' 
FROM (
    select count(*) as target from user 
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0) as p;

-- edits neither talkspace nor mainspace
SELECT CONCAT(FORMAT(IF(@numUsers=0,0,(target*100.0)/@numUsers),2),'%') 'edits neither talkspace nor mainspace' 
FROM (
    select count(*) as target from user 
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0) as p;

SELECT '- pages by namespace:' AS '';
SELECT namespace, count(page_id) AS 'count' FROM page GROUP BY namespace; 
SELECT '' AS '';

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

SELECT 'bots with most talkpage edits:' AS '';
SELECT username, talkpage_number_of_edits AS 'talkpage edits' 
FROM user
where bot is True
order by talkpage_number_of_edits desc 
limit 5;

SELECT 'users with most talkpage edits:' AS '';
SELECT username, talkpage_number_of_edits AS 'talkpage edits' 
FROM user 
where bot is null 
order by talkpage_number_of_edits desc limit 5;
SELECT '' AS '';

SELECT 'users with most reversions:' AS '';
SELECT username, reverted_edits 
FROM user 
where bot is null 
and username is not null 
order by reverted_edits desc 
limit 5;

SELECT 'bots with most reversions:' AS '';
SELECT username, reverted_edits 
FROM user 
where bot is True
order by reverted_edits desc 
limit 5;

SELECT 'ip users with most reversions:' AS '';
SELECT ip_address, reverted_edits 
FROM user 
where ip_address is not null 
order by reverted_edits desc 
limit 5;

select * from user where username = 'Bluerasberry' \G;

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
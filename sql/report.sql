SELECT 'How many:' AS '';
SELECT count(*) as '- users:' FROM user;
SELECT count(*) as '- users with over 100 edits:' FROM user where number_of_edits > 100;
SELECT count(*) as '- pages:' FROM page;
SELECT count(*) as '- edits:' FROM edit;
-- SELECT count(*) as '- IP users that edit talkpages:' FROM edit;
SELECT '' AS '';

SELECT 'Proportion of:' AS '';
    /* - edits containing bad words */
SELECT CONCAT(FORMAT(IF(main=0,0,(talk*100.0)/main),2),'%') as '- pages with talk pages:' From (SELECT (SELECT count(page_id) FROM page where namespace =0) as main,
(SELECT count(page_id) FROM page where namespace = 1) as talk) as proportion; 
SELECT '- partitions that are done vs error:' AS '';
SELECT status as 'job status', count(id) as 'count' FROM partition GROUP BY status; 
SELECT '' AS '';

SELECT 'Distribution of:' AS '';
SELECT '- users by number of edits:' AS '';
select (select count(*) from user where number_of_edits = 0) as 'no edits', (select count(*) from user where number_of_edits = 1) as '1 edit', (select count(*) from user where number_of_edits > 1 and number_of_edits <= 10) as '2-10 edits', (select count(*) from user where number_of_edits > 10 and number_of_edits <= 100) as '11-100 edits', (select count(*) from user where number_of_edits > 100) as '>100 edits';
SELECT '- pages by namespace:' AS '';
SELECT namespace, count(page_id) as 'count' FROM page GROUP BY namespace; 
SELECT '' AS '';

SELECT 'Size of database:' AS '';
SELECT table_schema AS "Database", SUM(data_length + index_length) / 1024 / 1024 / 1024 AS "Size (GB)" 
    FROM information_schema.TABLES GROUP BY table_schema;

/* need to add that user also edits mainspace */
/* maybe still keep number of edits? would be good for analysis */
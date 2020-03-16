select 'How many:' AS '';
select '  - users:' AS '';
select count(*) from user;
select '  - users with over 100 edits:' AS '';
select count(*) from user where number_of_edits > 100;
select '  - pages:' AS '';
select count(*) from page;
select '  - edits:' AS '';
select count(*) from edit;
select '' AS '';
select 'Proportion of:' AS '';
    /* - edits containing bad words */
select '  - partitions that are done vs error:' AS '';
SELECT status, count(id) FROM partition GROUP BY status; 
select '  - pages with talk pages:' AS '';
SELECT namespace, count(page_id) FROM page GROUP BY namespace; 
select '' AS '';
select 'Distribution of:' AS '';
select '  - users by number of edits:' AS '';
SELECT
    FLOOR( user.number_of_edits / stat.diff ) * stat.diff as range_start, 
    (FLOOR( user.number_of_edits / stat.diff ) +1) * stat.diff -1 as range_end, 
    count( user.number_of_edits ) as num_edits
FROM user, 
    (SELECT 
        ROUND((MAX( number_of_edits ) - MIN( number_of_edits ))/10) AS diff
    FROM user
    ) AS stat
GROUP BY FLOOR( user.number_of_edits / stat.diff );
select '' AS '';
select 'Size of database:' AS '';
SELECT table_schema AS "Database", SUM(data_length + index_length) / 1024 / 1024 / 1024 AS "Size (GB)" FROM information_schema.TABLES GROUP BY table_schema;

/* need to add that user also edits mainspace */
/* maybe still keep number of edits? would be good for analysis */


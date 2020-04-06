-- Manually created, but 90% there
-- See annotated version at https://docs.google.com/spreadsheets/d/16aVV2Wh7ezjwaGnoYtqU9bVHTXNBPwHwhX3oVctmTUM/edit#gid=1860359731

DROP TABLE IF EXISTS edit;

DROP TABLE IF EXISTS page;

DROP TABLE IF EXISTS user;

DROP TABLE IF EXISTS partition;

CREATE TABLE user (
    id int unsigned NOT NULL AUTO_INCREMENT,
    user_id int DEFAULT NULL,
    username varchar(255) binary DEFAULT NULL,
    ip_address varbinary(16) DEFAULT NULL,
    confirmed tinyint(1) DEFAULT NULL,
    user_special tinyint(1) DEFAULT NULL,
    bot tinyint(1) DEFAULT NULL,
    blocked tinyint(1) DEFAULT NULL,
    paid tinyint(1) DEFAULT NULL,
    user_page tinyint(1) DEFAULT NULL,
    user_talkpage tinyint(1) DEFAULT NULL,
    number_of_edits int unsigned NOT NULL DEFAULT '0',
    reverted_edits int unsigned DEFAULT '0',
    talkpage_number_of_edits int unsigned NOT NULL DEFAULT '0',
    talkpage_reverted_edits int unsigned DEFAULT '0',
    namespaces set('0','1','2','3','4','5','6','7','8','9','10','11','12','13',
        '14','15','-1','-2','100','101','118','119','710','711','828','829',
        '108','109','446','447','2300','2301','2302','2303') NOT NULL DEFAULT '',
    PRIMARY KEY (id),
    UNIQUE KEY username_UNIQUE (username),
    UNIQUE KEY ip_address_UNIQUE (ip_address)
);

/* create index */
CREATE INDEX userid_idx ON user (user_id);

/* check and trigger ? */
CREATE TABLE page (
    page_id INT NOT NULL,
    namespace smallint NOT NULL,
    title varchar(255) binary NOT NULL,
    file_name varchar(85) NOT NULL,
    number_of_edits int unsigned NOT NULL DEFAULT '0',
    PRIMARY KEY (page_id)
);

/* create index */
CREATE INDEX title_idx ON page (title);

CREATE TABLE edit (
    id int unsigned NOT NULL AUTO_INCREMENT,
    edit_id int DEFAULT NULL,
    edit_date datetime NOT NULL,
    page_id int DEFAULT NULL,
    user_table_id int unsigned NOT NULL,
    added text,
    deleted text,
    added_length MEDIUMINT,
    deleted_length MEDIUMINT, 
    blanking tinyint(1) DEFAULT NULL,
    comment_copyedit tinyint(1) DEFAULT NULL,
    comment_length tinyint(1) DEFAULT NULL,
    comment_personal_life tinyint(1) DEFAULT NULL,
    -- comment_spam decimal(4, 4) DEFAULT NULL,
    comment_special_chars decimal(4, 4) DEFAULT NULL,
    -- del_bias mediumint DEFAULT NULL,
    del_words mediumint DEFAULT NULL,
    -- ins_bias decimal(4, 4) DEFAULT NULL,
    ins_capitalization decimal(4, 4) DEFAULT NULL,
    -- ins_compressibility decimal(4, 4) DEFAULT NULL,
    ins_digits decimal(4, 4) DEFAULT NULL,
    ins_external_link smallint DEFAULT NULL,
    ins_internal_link smallint DEFAULT NULL,
    ins_longest_character_sequence smallint DEFAULT NULL,
    ins_longest_inserted_word smallint DEFAULT NULL,
    ins_pronouns decimal(4, 4) DEFAULT NULL,
    -- ins_sex decimal(4, 4) DEFAULT NULL,
    ins_special_chars decimal(4, 4) DEFAULT NULL,
    -- ins_special_words decimal(4, 4) DEFAULT NULL,
    ins_vulgarity tinyint(1) DEFAULT NULL,
    ins_whitespace decimal(4, 4) DEFAULT NULL,
    -- ins_wp decimal(4, 4) DEFAULT NULL,
    -- kldnew2old decimal(5, 5) DEFAULT NULL,
    reverted tinyint(1) DEFAULT 0,
    PRIMARY KEY (id),
    KEY user_idx (user_table_id),
    KEY page_idx (page_id),
    CONSTRAINT page FOREIGN KEY (page_id) REFERENCES page (page_id),
    CONSTRAINT user FOREIGN KEY (user_table_id) REFERENCES user (id)
);

/* create index */
CREATE INDEX editid_idx ON edit (edit_id);
CREATE INDEX editdate_idx ON edit (edit_date);

CREATE TABLE partition (
    id int unsigned NOT NULL AUTO_INCREMENT,
    file_name varchar(85) NOT NULL,
    status enum('todo','running','failed','restarted','failed again','done',
        'cleaned') NOT NULL DEFAULT 'todo',
    error text,
    start_time_1 timestamp NULL DEFAULT '0000-00-00 00:00:00',
    end_time_1 timestamp NULL DEFAULT '0000-00-00 00:00:00',
    start_time_2 timestamp NULL DEFAULT '0000-00-00 00:00:00',
    end_time_2 timestamp NULL DEFAULT '0000-00-00 00:00:00',
    PRIMARY KEY (id)
);
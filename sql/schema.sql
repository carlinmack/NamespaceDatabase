-- Manually created, but 90% there
-- See annotated version at https://docs.google.com/spreadsheets/d/16aVV2Wh7ezjwaGnoYtqU9bVHTXNBPwHwhX3oVctmTUM/edit#gid=1860359731

CREATE TABLE edit (
	id INT unsigned NOT NULL AUTO_INCREMENT,
	namespace SMALLINT NOT NULL,
	edit_id INT,
	edit_date DATETIME NOT NULL,
	page_id INT,
	user_id INT,
    ip_address VARBINARY(16),
	added TEXT,
	deleted TEXT,
    blanking BOOLEAN,
    comment_copyedit BOOLEAN,
    comment_length BOOLEAN,
    comment_personal_life BOOLEAN,
    comment_spam NUMERIC(4,4),
    comment_special_chars NUMERIC(4,4),
    del_bias MEDIUMINT,
    del_words MEDIUMINT,
    ins_bias NUMERIC(4,4),
    ins_capitalization NUMERIC(4,4),
    ins_compressibility NUMERIC(4,4),
    ins_digits NUMERIC(4,4),
    ins_external_link SMALLINT,
    ins_internal_link SMALLINT,
    ins_longest_character_sequence SMALLINT,
    ins_longest_inserted_word SMALLINT,
    ins_pronouns NUMERIC(4,4),
    ins_sex NUMERIC(4,4),
    ins_special_chars NUMERIC(4,4),
    ins_special_words NUMERIC(4,4),
    ins_vulgarism NUMERIC(4,4),
    ins_whitespace NUMERIC(4,4),
    ins_wp NUMERIC(4,4),
    kldnew2old NUMERIC(5,5),
	PRIMARY KEY (id)
);


CREATE TABLE page (
	id INT unsigned NOT NULL AUTO_INCREMENT,
	page_id INT,
    title TEXT,
	PRIMARY KEY (id)
);


CREATE TABLE partition (
	id INT unsigned NOT NULL AUTO_INCREMENT,
	file_name VARCHAR(85) NOT NULL,
	status ENUM('todo', 'running', 'failed', 'restarted', 'failed again', 'done', 'cleaned') NOT NULL DEFAULT 'todo',
	error TEXT,
	start_time_1 TIMESTAMP DEFAULT 0,
	end_time_1 TIMESTAMP DEFAULT 0,
	start_time_2 TIMESTAMP DEFAULT 0,
	end_time_2 TIMESTAMP DEFAULT 0,
	PRIMARY KEY (id)
);


CREATE TABLE user (
	id INT unsigned NOT NULL AUTO_INCREMENT,
	user_id INT,
    username VARCHAR(85),
    ip_address VARBINARY(16),
    confirmed BOOLEAN,
    user_special BOOLEAN,
    bot BOOLEAN,
    blocked BOOLEAN,
    paid BOOLEAN,
    user_page BOOLEAN,
    user_talkpage BOOLEAN,
    number_of_edits INT unsigned,
    reverted_edits INT unsigned,
	PRIMARY KEY (id)
);
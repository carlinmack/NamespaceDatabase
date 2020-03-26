# Table edit

| Field                          | Type             | Null | Key | Default | Extra          |
|--------------------------------|------------------|------|-----|---------|----------------|
| id                             | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| edit_id                        | int(11)          | YES  |     | NULL    |                |
| edit_date                      | datetime         | NO   |     | NULL    |                |
| page_id                        | int(11)          | YES  | MUL | NULL    |                |
| user_table_id                  | int(10) unsigned | NO   | MUL | NULL    |                |
| added                          | text             | YES  |     | NULL    |                |
| deleted                        | text             | YES  |     | NULL    |                |
| added_length                   | mediumint(9)     | YES  |     | NULL    |                |
| deleted_length                 | mediumint(9)     | YES  |     | NULL    |                |
| blanking                       | tinyint(1)       | YES  |     | NULL    |                |
| comment_copyedit               | tinyint(1)       | YES  |     | NULL    |                |
| comment_length                 | tinyint(1)       | YES  |     | NULL    |                |
| comment_personal_life          | tinyint(1)       | YES  |     | NULL    |                |
| comment_special_chars          | decimal(4,4)     | YES  |     | NULL    |                |
| del_words                      | mediumint(9)     | YES  |     | NULL    |                |
| ins_capitalization             | decimal(4,4)     | YES  |     | NULL    |                |
| ins_digits                     | decimal(4,4)     | YES  |     | NULL    |                |
| ins_external_link              | smallint(6)      | YES  |     | NULL    |                |
| ins_internal_link              | smallint(6)      | YES  |     | NULL    |                |
| ins_longest_character_sequence | smallint(6)      | YES  |     | NULL    |                |
| ins_longest_inserted_word      | smallint(6)      | YES  |     | NULL    |                |
| ins_pronouns                   | decimal(4,4)     | YES  |     | NULL    |                |
| ins_special_chars              | decimal(4,4)     | YES  |     | NULL    |                |
| ins_whitespace                 | decimal(4,4)     | YES  |     | NULL    |                |
| reverted                       | tinyint(1)       | YES  |     | 0       |                |

----------------------------------------------------------------------

# Tabel page 

| Field     | Type        | Null | Key | Default | Extra |
|-----------|-------------|------|-----|---------|-------|
| page_id   | int(11)     | NO   | PRI | NULL    |       |
| namespace | smallint(6) | NO   |     | NULL    |       |
| title     | text        | YES  |     | NULL    |       |
| file_name | varchar(85) | NO   |     | NULL    |       |

----------------------------------------------------------------------

# Table partition 

| Field        | Type                                                                        | Null | Key | Default             | Extra          |
|--------------|-----------------------------------------------------------------------------|------|-----|---------------------|----------------|
| id           | int(10) unsigned                                                            | NO   | PRI | NULL                | auto_increment |
| file_name    | varchar(85)                                                                 | NO   |     | NULL                |                |
| status       | enum('todo','running','failed','restarted','failed again','done','cleaned') | NO   |     | todo                |                |
| error        | text                                                                        | YES  |     | NULL                |                |
| start_time_1 | timestamp                                                                   | YES  |     | 0000-00-00 00:00:00 |                |
| end_time_1   | timestamp                                                                   | YES  |     | 0000-00-00 00:00:00 |                |
| start_time_2 | timestamp                                                                   | YES  |     | 0000-00-00 00:00:00 |                |
| end_time_2   | timestamp                                                                   | YES  |     | 0000-00-00 00:00:00 |                |

----------------------------------------------------------------------

# Table user

| Field                    | Type                                                                                                                                                                                     | Null | Key | Default | Extra          |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|-----|---------|----------------|
| id                       | int(10) unsigned                                                                                                                                                                         | NO   | PRI | NULL    | auto_increment |
| user_id                  | int(11)                                                                                                                                                                                  | YES  |     | NULL    |                |
| username                 | varchar(85)                                                                                                                                                                              | YES  | UNI | NULL    |                |
| ip_address               | varbinary(16)                                                                                                                                                                            | YES  | UNI | NULL    |                |
| confirmed                | tinyint(1)                                                                                                                                                                               | YES  |     | NULL    |                |
| user_special             | tinyint(1)                                                                                                                                                                               | YES  |     | NULL    |                |
| bot                      | tinyint(1)                                                                                                                                                                               | YES  |     | NULL    |                |
| blocked                  | tinyint(1)                                                                                                                                                                               | YES  |     | NULL    |                |
| paid                     | tinyint(1)                                                                                                                                                                               | YES  |     | NULL    |                |
| user_page                | tinyint(1)                                                                                                                                                                               | YES  |     | NULL    |                |
| user_talkpage            | tinyint(1)                                                                                                                                                                               | YES  |     | NULL    |                |
| number_of_edits          | int(10) unsigned                                                                                                                                                                         | NO   |     | 0       |                |
| reverted_edits           | int(10) unsigned                                                                                                                                                                         | YES  |     | 0       |                |
| talkpage_number_of_edits | int(10) unsigned                                                                                                                                                                         | NO   |     | 0       |                |
| talkpage_reverted_edits  | int(10) unsigned                                                                                                                                                                         | YES  |     | 0       |                |
| namespaces               | set('0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','-1','-2','100','101','118','119','710','711','828','829','108','109','446','447','2300','2301','2302','2303') | NO   |     |         |                |

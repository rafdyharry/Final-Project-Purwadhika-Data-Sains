-- Untuk cari tau di mana directory untuk menyimpan data 
SHOW VARIABLES LIKE 'secure_file_priv';

-- Pindah file ke directory tersebut

-- lalu run query ini untuk mengimport data
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\tips.csv'
INTO TABLE tips
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
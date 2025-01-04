CREATE DATABASE IF NOT EXISTS translations_db;

USE translations_db;

CREATE TABLE translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    source_text VARCHAR(255) NOT NULL,
    translated_text VARCHAR(255) NOT NULL
);

INSERT INTO translations (source_language, target_language, source_text, translated_text)
VALUES
    ('en', 'tl', 'hello', 'kamusta'),
    ('en', 'ceb', 'hello', 'kumusta'),
    ('en', 'ilo', 'hello', 'nagkamusta'),
    ('tl', 'en', 'kamusta', 'hello'),
    ('ceb', 'en', 'kumusta', 'hello'),
    ('ilo', 'en', 'nagkamusta', 'hello');
    
SELECT * from translations;

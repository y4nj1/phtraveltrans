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
    -- English to Tagalog
    ('en', 'tl', 'How far is it?', 'Gaano pa kalayo?'),
    ('en', 'tl', 'Where is the nearest [hotel/restaurant/bathroom]?', 'Saan ang pinakamalapit na [hotel/restawran/banyo]?'),
    ('en', 'tl', 'Do you have any recommendations for a good place to visit?', 'May mairerekomenda ka bang magandang pasyalan?'),
    ('en', 'tl', 'How far is it from here?', 'Gaano kalayo mula dito?'),
    ('en', 'tl', 'I’m lost.', 'Naliligaw ako.'),
    ('en', 'tl', 'Can you help me?', 'Puwede mo ba akong tulungan?'),
    ('en', 'tl', 'Can you give me directions to [place]?', 'Puwede mo ba akong bigyan ng direksyon papunta sa [place]?'),
    ('en', 'tl', 'Thank you very much', 'Maraming Salamat'),
    ('en', 'tl', 'Good morning', 'Magandang Umaga'),

    -- Tagalog to English
    ('tl', 'en', 'Gaano pa kalayo?', 'How far is it?'),
    ('tl', 'en', 'Saan ang pinakamalapit na [hotel/restawran/banyo]?', 'Where is the nearest [hotel/restaurant/bathroom]?'),
    ('tl', 'en', 'May mairerekomenda ka bang magandang pasyalan?', 'Do you have any recommendations for a good place to visit?'),
    ('tl', 'en', 'Gaano kalayo mula dito?', 'How far is it from here?'),
    ('tl', 'en', 'Naliligaw ako.', 'I’m lost.'),
    ('tl', 'en', 'Puwede mo ba akong tulungan?', 'Can you help me?'),
    ('tl', 'en', 'Puwede mo ba akong bigyan ng direksyon papunta sa [place]?', 'Can you give me directions to [place]?'),
    ('tl', 'en', 'Maraming Salamat', 'Thank you very much'),
    ('tl', 'en', 'Magandang Umaga', 'Good morning'),

    -- English to Ilokano
    ('en', 'ilo', 'How far is it?', 'Kasano pay ti kaadayo na?'),
    ('en', 'ilo', 'Where is the nearest [hotel/restaurant/bathroom]?', 'Sadino ti ayan ti kaasitgan nga [hotel/restawran/banyo]?'),
    ('en', 'ilo', 'Do you have any recommendations for a good place to visit?', 'Mabalin kadi nga irekomendayo ti aniaman a nasayaat a lugar a pagpasyaran?'),
    ('en', 'ilo', 'How far is it from here?', 'Kasano ti kaadayo na manipud ditoy?'),
    ('en', 'ilo', 'I’m lost.', 'Nayaw-awanak.'),
    ('en', 'ilo', 'Can you help me?', 'Mabalin kadi a tulungannak?'),
    ('en', 'ilo', 'Can you give me directions to [place]?', 'Mabalin kadi nga ikkannak iti direksiyon nga agturong iti [place]?'),
    ('en', 'ilo', 'Thank you very much', 'Agyaman ak la unay'),
    ('en', 'ilo', 'Good morning', 'Naimbag a bigat'),

    -- Ilokano to English
    ('ilo', 'en', 'Kasano pay ti kaadayo na?', 'How far is it?'),
    ('ilo', 'en', 'Sadino ti ayan ti kaasitgan nga [hotel/restawran/banyo]?', 'Where is the nearest [hotel/restaurant/bathroom]?'),
    ('ilo', 'en', 'Mabalin kadi nga irekomendayo ti aniaman a nasayaat a lugar a pagpasyaran?', 'Do you have any recommendations for a good place to visit?'),
    ('ilo', 'en', 'Kasano ti kaadayo na manipud ditoy?', 'How far is it from here?'),
    ('ilo', 'en', 'Nayaw-awanak.', 'I’m lost.'),
    ('ilo', 'en', 'Mabalin kadi a tulungannak?', 'Can you help me?'),
    ('ilo', 'en', 'Mabalin kadi nga ikkannak iti direksiyon nga agturong iti [place]?', 'Can you give me directions to [place]?'),
    ('ilo', 'en', 'Agyaman ak la unay', 'Thank you very much'),
    ('ilo', 'en', 'Naimbag a bigat', 'Good morning'),

    -- English to Cebuano
    ('en', 'ceb', 'How far is it?', 'Paywan pa bala karayo?'),
    ('en', 'ceb', 'Where is the nearest [hotel/restaurant/bathroom]?', 'Sadin ang pinaka marapit nga [Hotel/restaurant/Rigya]?'),
    ('en', 'ceb', 'Do you have any recommendations for a good place to visit?', 'Ano bala mong ma Rekomenda nga Lugar nga manamit anayanan?'),
    ('en', 'ceb', 'How far is it from here?', 'Paywan karayo alin digya payan duto?'),
    ('en', 'ceb', 'I’m lost.', 'Nagtalang ako.'),
    ('en', 'ceb', 'Can you help me?', 'Pwede mo ako buligan?'),
    ('en', 'ceb', 'Can you give me directions to [place]?', 'Pwede mo bala itudlo ang Dalan payan sa lugar ngato?'),
    ('en', 'ceb', 'Thank you very much', 'Duro duro gid nga salamat'),
    ('en', 'ceb', 'Good morning', 'Mayad nga aga Kanindo'),

    -- Cebuano to English
    ('ceb', 'en', 'Paywan pa bala karayo?', 'How far is it?'),
    ('ceb', 'en', 'Sadin ang pinaka marapit nga [Hotel/restaurant/Rigya]?', 'Where is the nearest [hotel/restaurant/bathroom]?'),
    ('ceb', 'en', 'Ano bala mong ma Rekomenda nga Lugar nga manamit anayanan?', 'Do you have any recommendations for a good place to visit?'),
    ('ceb', 'en', 'Paywan karayo alin digya payan duto?', 'How far is it from here?'),
    ('ceb', 'en', 'Nagtalang ako.', 'I’m lost.'),
    ('ceb', 'en', 'Pwede mo ako buligan?', 'Can you help me?'),
    ('ceb', 'en', 'Pwede mo bala itudlo ang Dalan payan sa lugar ngato?', 'Can you give me directions to [place]?'),
    ('ceb', 'en', 'Duro duro gid nga salamat', 'Thank you very much'),
    ('ceb', 'en', 'Mayad nga aga Kanindo', 'Good morning'),

    -- Tagalog to Ilokano
    ('tl', 'ilo', 'Gaano pa kalayo?', 'Kasano pay ti kaadayo na?'),
    ('tl', 'ilo', 'Saan ang pinakamalapit na [hotel/restawran/banyo]?', 'Sadino ti ayan ti kaasitgan nga [hotel/restawran/banyo]?'),
    ('tl', 'ilo', 'May mairerekomenda ka bang magandang pasyalan?', 'Mabalin kadi nga irekomendayo ti aniaman a nasayaat a lugar a pagpasyaran?'),
    ('tl', 'ilo', 'Gaano kalayo mula dito?', 'Kasano ti kaadayo na manipud ditoy?'),
    ('tl', 'ilo', 'Naliligaw ako.', 'Nayaw-awanak.'),
    ('tl', 'ilo', 'Puwede mo ba akong tulungan?', 'Mabalin kadi a tulungannak?'),
    ('tl', 'ilo', 'Puwede mo ba akong bigyan ng direksyon papunta sa [place]?', 'Mabalin kadi nga ikkannak iti direksiyon nga agturong iti [place]?'),
    ('tl', 'ilo', 'Maraming Salamat', 'Agyaman ak la unay'),
    ('tl', 'ilo', 'Magandang Umaga', 'Naimbag a bigat'),

    -- Ilokano to Tagalog
    ('ilo', 'tl', 'Kasano pay ti kaadayo na?', 'Gaano pa kalayo?'),
    ('ilo', 'tl', 'Sadino ti ayan ti kaasitgan nga [hotel/restawran/banyo]?', 'Saan ang pinakamalapit na [hotel/restawran/banyo]?'),
    ('ilo', 'tl', 'Mabalin kadi nga irekomendayo ti aniaman a nasayaat a lugar a pagpasyaran?', 'May mairerekomenda ka bang magandang pasyalan?'),
    ('ilo', 'tl', 'Kasano ti kaadayo na manipud ditoy?', 'Gaano kalayo mula dito?'),
    ('ilo', 'tl', 'Nayaw-awanak.', 'Naliligaw ako.'),
    ('ilo', 'tl', 'Mabalin kadi a tulungannak?', 'Puwede mo ba akong tulungan?'),
    ('ilo', 'tl', 'Mabalin kadi nga ikkannak iti direksiyon nga agturong iti [place]?', 'Puwede mo ba akong bigyan ng direksyon papunta sa [place]?'),
    ('ilo', 'tl', 'Agyaman ak la unay', 'Maraming Salamat'),
    ('ilo', 'tl', 'Naimbag a bigat', 'Magandang Umaga'),

    -- Tagalog to Cebuano
    ('tl', 'ceb', 'Gaano pa kalayo?', 'Paywan pa bala karayo?'),
    ('tl', 'ceb', 'Saan ang pinakamalapit na [hotel/restawran/banyo]?', 'Sadin ang pinaka marapit nga [Hotel/restaurant/Rigya]?'),
    ('tl', 'ceb', 'May mairerekomenda ka bang magandang pasyalan?', 'Ano bala mong ma Rekomenda nga Lugar nga manamit anayanan?'),
    ('tl', 'ceb', 'Gaano kalayo mula dito?', 'Paywan karayo alin digya payan duto?'),
    ('tl', 'ceb', 'Naliligaw ako.', 'Nagtalang ako.'),
    ('tl', 'ceb', 'Puwede mo ba akong tulungan?', 'Pwede mo ako buligan?'),
    ('tl', 'ceb', 'Puwede mo ba akong bigyan ng direksyon papunta sa [place]?', 'Pwede mo bala itudlo ang Dalan payan sa lugar ngato?'),
    ('tl', 'ceb', 'Maraming Salamat', 'Duro duro gid nga salamat'),
    ('tl', 'ceb', 'Magandang Umaga', 'Mayad nga aga Kanindo'),

    -- Cebuano to Tagalog
    ('ceb', 'tl', 'Paywan pa bala karayo?', 'Gaano pa kalayo?'),
    ('ceb', 'tl', 'Sadin ang pinaka marapit nga [Hotel/restaurant/Rigya]?', 'Saan ang pinakamalapit na [hotel/restawran/banyo]?'),
    ('ceb', 'tl', 'Ano bala mong ma Rekomenda nga Lugar nga manamit anayanan?', 'May mairerekomenda ka bang magandang pasyalan?'),
    ('ceb', 'tl', 'Paywan karayo alin digya payan duto?', 'Gaano kalayo mula dito?'),
    ('ceb', 'tl', 'Nagtalang ako.', 'Naliligaw ako.'),
    ('ceb', 'tl', 'Pwede mo ako buligan?', 'Puwede mo ba akong tulungan?'),
    ('ceb', 'tl', 'Pwede mo bala itudlo ang Dalan payan sa lugar ngato?', 'Puwede mo ba akong bigyan ng direksyon papunta sa [place]?'),
    ('ceb', 'tl', 'Duro duro gid nga salamat', 'Maraming Salamat'),
    ('ceb', 'tl', 'Mayad nga aga Kanindo', 'Magandang Umaga'),

	-- Cebuano to Ilokano
    ('ceb', 'ilo', 'Paywan pa bala karayo?', 'Kasano pay ti kaadayo na?'),
    ('ceb', 'ilo', 'Sadin ang pinaka marapit nga [Hotel/restaurant/Rigya]?', 'Sadino ti ayan ti kaasitgan nga [hotel/restawran/banyo]?'),
    ('ceb', 'ilo', 'Ano bala mong ma Rekomenda nga Lugar nga manamit anayanan?', 'Mabalin kadi nga irekomendayo ti aniaman a nasayaat a lugar a pagpasyaran?'),
    ('ceb', 'ilo', 'Paywan karayo alin digya payan duto?', 'Kasano ti kaadayo na manipud ditoy?'),
    ('ceb', 'ilo', 'Nagtalang ako.', 'Nayaw-awanak.'),
    ('ceb', 'ilo', 'Pwede mo ako buligan?', 'Mabalin kadi a tulungannak?'),
    ('ceb', 'ilo', 'Pwede mo bala itudlo ang Dalan payan sa lugar ngato?', 'Mabalin kadi nga ikkannak iti direksiyon nga agturong iti [place]?'),
    ('ceb', 'ilo', 'Duro duro gid nga salamat', 'Agyaman ak la unay'),
    ('ceb', 'ilo', 'Mayad nga aga Kanindo', 'Naimbag a bigat'),
    
	-- Ilokano to Cebuano
    ('ilo', 'ceb', 'Kasano pay ti kaadayo na?', 'Paywan pa bala karayo?'),
    ('ilo', 'ceb', 'Sadino ti ayan ti kaasitgan nga [hotel/restawran/banyo]?', 'Sadin ang pinaka marapit nga [Hotel/restaurant/Rigya]?'),
    ('ilo', 'ceb', 'Mabalin kadi nga irekomendayo ti aniaman a nasayaat a lugar a pagpasyaran?', 'Ano bala mong ma Rekomenda nga Lugar nga manamit anayanan?'),
    ('ilo', 'ceb', 'Kasano ti kaadayo na manipud ditoy?', 'Paywan karayo alin digya payan duto?'),
    ('ilo', 'ceb', 'Nayaw-awanak.', 'Nagtalang ako.'),
    ('ilo', 'ceb', 'Mabalin kadi a tulungannak?', 'Pwede mo ako buligan?'),
    ('ilo', 'ceb', 'Mabalin kadi nga ikkannak iti direksiyon nga agturong iti [place]?', 'Pwede mo bala itudlo ang Dalan payan sa lugar ngato?'),
    ('ilo', 'ceb', 'Agyaman ak la unay', 'Duro duro gid nga salamat'),
    ('ilo', 'ceb', 'Naimbag a bigat', 'Mayad nga aga Kanindo');
    
SELECT * from translations;

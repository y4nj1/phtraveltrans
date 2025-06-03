import speech_recognition as sr
import re
from googletrans import Translator
import mysql.connector

# Initialize recognizer
recognizer = sr.Recognizer()
translator = Translator()

def fetch_translation(source_text, source_lang, target_lang):
    """Fetch translation from the database."""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root", 
            password="pHtrans2025",  
            database="translations_db"  
        )

        cursor = connection.cursor()
        query = """
            SELECT translated_text
            FROM translations
            WHERE source_language = %s AND target_language = %s AND source_text = %s
        """
        cursor.execute(query, (source_lang, target_lang, source_text.lower()))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the translated text
        else:
            return source_text  # Fallback to the original text if no translation found

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return source_text

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def translate_text(source_text, source_lang, target_lang):
    """Translate text using database first, fallback to Google Translate API."""
    # First, try fetching translation from the database
    translation = fetch_translation(source_text, source_lang, target_lang)
    if translation != source_text:
        return translation

    # If not found in the database, use Google Translate API
    try:
        translated = translator.translate(source_text, src=source_lang, dest=target_lang)
        return translated.text
    except Exception as e:
        print(f"Google Translate Error: {e}")
        return source_text

def normalize_transcription(text, language):
    """Normalize and correct common transcription errors."""
    corrections = {
        "ceb": {  # Cebuano corrections
            "my ion gabby": "maayong gabi",
            "Malayalam Gabby": "maayong gabi",
            "may I am Gabby": "maayong gabi",
            "I'm going to be": "maayong gabi",
            "I am going to be": "maayong gabi",
            "my own baby": "maayong gabi",
            "my eye on Gabby": "maayong gabi",
            "my eye on the bee": "maayong gabi",
            "Mayan Gabby": "maayong gabi",
            "may I am going to be": "maayong gabi",
            "Myung Gabby" : "maayong gabi",
            "my own Gabby" : "maayong gabi",
            "myON Gabby" : "maayong gabi",
            "my uncle bee" : "maayong gabi",
            "maayuga" : "maayong gabi",
            "my aisle Gabby" : "maayong gabi",
            "my uncle" : "maayong gabi",
            "Mario Gabby" : "maayong gabi",
            "miami" : "maayong gabi",
            "my iron gab": "maayong gabi",
            "my iron baby": "maayong gabi",
            "my iron": "maayong gabi",
            "my are you going to": "maayong gabi",
            "my eye on the beat": "maayong gabi",
            "but I don't got": "maayong gabi",
            "maayonga": "maayong gabi",
            "maayong": "maayong gabi",
            "mayong gabby": "maayong gabi",
            "my young gabby": "maayong gabi",
            "my young baby": "maayong gabi",
            "mario gabi": "maayong gabi",
            "my young bee": "maayong gabi",
            "malayong gabi": "maayong gabi",
            "my young bunny": "maayong gabi",
            "my younger" : "maayong gabi",
            "maayong gabi gabi": "maayong gabi", 
            "but I": "maayong gabi",
            "but I don't": "maayong gabi",  
            "but maayong hapon going to": "maayong gabi", 
            "Mario Gab": "maayong gabi", 
            
            "maayong happen": "maayong hapon",
            "mayong happen": "maayong hapon",
            "may I don't happen": "maayong hapon",
            "I don't happen": "maayong hapon",
            "my iron happen": "maayong hapon",
            "my own happened": "maayong hapon",
            "my own happen": "maayong hapon",
            "Malayalam happened" : "maayong hapon",
            "my own husband" : "maayong hapon",
            "don't happen": "maayong hapon",
            "I am": "maayong hapon",
            "may i am happen": "maayong hapon",
            "my oil happened": "maayong hapon",
            "my young happen": "maayong hapon",
            "malayong happen": "maayong hapon",
            "my young hop on": "maayong hapon",
            "my young hopping": "maayong hapon",
            "now you have": "maayong hapon", 
            "I don't have": "maayong hapon", 
            "smile happen": "maayong hapon", 
            "why you happen": "maayong hapon", 
            "my what happened": "maayong hapon",
            "maayong hapon happy": "maayong hapon", 
            "why you have": "maayong hapon", 
            "but maayong hapon": "maayong hapon",

            "my iron bunting": "Maayong buntag",
            "Malayalam buntag": "Maayong buntag",
            "my iron contact": "Maayong buntag",
            "my iron buntag": "Maayong buntag",
            "but I want": "Maayong buntag",
            "my own contact": "Maayong buntag",
            "Michael Jackson": "Maayong buntag",
            "my own contact": "Maayong buntag",
            "my ion buntag": "Maayong buntag",
            "Mayan buntag": "Maayong buntag",
            "Mario bull tag": "Maayong buntag",
            "my own bun tag": "Maayong buntag",
            "my own buntag": "Maayong buntag",
            "my young buntag" : "Maayong buntag",
            "my own bunting" : "Maayong buntag",
            "I am going to": "maayong buntag",
            "my iron": "maayong buntag",
            "my eye on": "maayong buntag",
            "my young bunta": "maayong buntag",
            "my youngin tag": "maayong buntag",
            "malayong buntag": "maayong buntag",
            "my young contact": "maayong buntag",
            "my young gun tag": "maayong buntag",
            "fine winter": "maayong buntag",
            "Mario and": "maayong buntag",
            "Maya Winter": "maayong buntag",
            "my window": "maayong buntag",
            "mine winter": "maayong buntag",
            "Mylanta": "maayong buntag",
            "my winter": "maayong buntag",
            
            "dog hung salamat": "Daghang salamat",
            "dog Haus salamat": "Daghang salamat",
            "the gang salamat": "Daghang salamat",
            "Doug hung salamat": "Daghang salamat",
            "Doug Hahn salamat": "Daghang salamat",
            "the Khan salamat": "Daghang salamat",
            "Dog House salamat": "Daghang salamat",
            "Doug ham salamat": "Daghang salamat",
            "Doug hung salam": "Daghang salamat",
            "background salam": "Daghang salamat",
            "Oklahoma Salam": "Daghang salamat",
            "the gun Salam": "Daghang salamat",
            "Doug hamsalam": "Daghang salamat",
            "the gang": "Daghang salamat",
            "Dog House Alam": "Daghang salamat",
            "doghang salamat": "daghang salamat",
            "dogon salamat": "daghang salamat",
            "dagon salamat": "daghang salamat",
            "dugong salamat": "daghang salamat",
            "dug in salamat": "daghang salamat",
            "the grand Salama": "daghang salamat",
            "the grand salamat": "daghang salamat",
            "the gas alarm": "daghang salamat",
            "Downtown Cinema": "daghang salamat",
            "Big Ang salamat": "daghang salamat",
            "Nikon Salam": "daghang salamat",
            
#===============================================            
            "pwede kunimoto baingan": "Pwede ko nimo tabangan?",
            "puede kunimoto baingan": "Pwede ko nimo tabangan?",
            "play the kanamoto baingan": "Pwede ko nimo tabangan?",
            "wendigo Nemo Obama": "Pwede ko nimo tabangan?",
            "Freddy call Nemo taban": "Pwede ko nimo tabangan?",
            "felico Nemo about": "Pwede ko nimo tabangan?",
            "wendigo Nemo about": "Pwede ko nimo tabangan?",
            "pretty funny": "Pwede ko nimo tabangan?",
            "political Nemo about": "Pwede ko nimo tabangan?",
            "where they go anymore about": "Pwede ko nimo tabangan?",
            "ready for me more about": "Pwede ko nimo tabangan?",
            "where to go anymore": "Pwede ko nimo tabangan?",
            "wendigo Nemo the band": "Pwede ko nimo tabangan?",
            "where they go anymore about": "Pwede ko nimo tabangan?",
            "predico Nemo the bang": "Pwede ko nimo tabangan?",
            "lady bunny": "Pwede ko nimo tabangan?",
            "ready to go anymore": "Pwede ko nimo tabangan?",
            "wendigo animal": "Pwede ko nimo tabangan?",
            "when you go anymore about": "Pwede ko nimo tabangan?",
            "Pwede ko nimo tabangan? about": "Pwede ko nimo tabangan?",
            "wendigo Nemo taban": "Pwede ko nimo tabangan?",
            "21 Nemo taban": "Pwede ko nimo tabangan?",
#===============================================  
            "baingan": "tabangan",
            "the Batman": "tabangan",
            "cabangon": "tabangan",
            "the island": "tabangan",
            "the Bal": "tabangan",
            "the balance": "tabangan",
            "the ball": "tabangan",
            
            "delete": "Dili",
            "Lily": "Dili",
            "Billy": "Dili",
            
            "oh oh": "Oo",
            "uh-oh": "Oo",
            
            "weather for Caballo": "Wala ko kabalo",
            "hola como Caballo": "Wala ko kabalo",
            "malaco Cavallo": "Wala ko kabalo",
            "hola como": "Wala ko kabalo",
            
            
        },
        "tl": {  # Tagalog corrections
            "ko musta": "kumusta",
            "pa alam": "paalam",
        },
        "ilo": {  # Ilokano corrections
            "nagmayat nga aldaw": "naimbag nga aldaw",
            "name bug now": "naimbag nga aldaw",
            "name but now": "naimbag nga aldaw",
            "I'm back": "naimbag nga aldaw",
            "same but I don't know": "naimbag nga aldaw",
            "same bug not to do": "naimbag nga aldaw",
            "same but": "naimbag nga aldaw",
            "same but not": "naimbag nga aldaw",
            "same button": "naimbag nga aldaw",
            "same Buckner I don't know": "naimbag nga aldaw",
            "same button I": "naimbag nga aldaw",
            "playing bad night": "naimbag nga aldaw",
            "playing but now": "naimbag nga aldaw",
            "magnol": "naimbag nga aldaw",
            "name bug n": "naimbag nga aldaw",
            "name magn": "naimbag nga aldaw",
            "same bug": "naimbag nga aldaw",
            "nothing bug not as though": "naimbag nga aldaw",
            "name button": "naimbag nga aldaw",
            "name Magno": "naimbag nga aldaw",
            "name Magna": "naimbag nga aldaw",

            "9 bag Abigail" : "Naimbag a bigat",
            "play bug a bigot" : "Naimbag a bigat",
            "naimbag a bigot" : "Naimbag a bigat",
            "9 bug a bigot" : "Naimbag a bigat",
            "name bag Abigail" : "Naimbag a bigat",
            "nothing but a bigot" : "Naimbag a bigat",
            "play Abigail" : "Naimbag a bigat",
            "9 bag of bigot" : "Naimbag a bigat",
            "name bag of bigot" : "Naimbag a bigat",
            "name but a bigger" : "Naimbag a bigat",
            "rainbow Abigail" : "Naimbag a bigat",
            "Abigail" : "Naimbag a bigat",
            "my inbox Abigail" : "Naimbag a bigat",
            "the imbag a big": "naimbag a bigat",
            "bug a bugatt": "naimbag a bigat",
            "making bug a big": "naimbag a bigat", 
            "bugabi got": "naimbag a bigat",
            "name bug a bigot": "naimbag a bigat",
            "nothing bug naimbag a bigat": "naimbag a bigat",
            "nothing bug a bugatt": "naimbag a bigat",
            "nothing bug a bug": "naimbag a bigat",
            "nothing bug": "naimbag a bigat",
            "nothing but happy God": "naimbag a bigat",
            "humbug": "naimbag a bigat",
            "I'm back a bigot": "naimbag a bigat",
            "but a big cat": "naimbag a bigat",
            "nambag a bigot": "naimbag a bigat",
            "i'm back and be good": "naimbag a bigat",
            "iron bag a big": "naimbag a bigat",
            "name back a big": "naimbag a bigat",
            "nambag a big": "naimbag a bigat",
            "name bug abig": "naimbag a bigat",
            "same bag abig": "naimbag a bigat",
            "laying bug Naimbag a bigat": "naimbag a bigat",
            "name bug Naimbag a bigat": "naimbag a bigat",
            "name Bugaboo": "naimbag a bigat",
            "nothing bug": "naimbag a bigat",

            "playing back Amal" : "Naimbag a malem",
            "name of Amalie" : "Naimbag a malem",
            "play Eminem" : "Naimbag a malem",
            "nightmare lemon" : "Naimbag a malem",
            "nightmare am" : "Naimbag a malem",
            "name back on my name" : "Naimbag a malem",
            "nightmare" : "Naimbag a malem",
            "play Bob Marley" : "Naimbag a malem",
            "name of Amal" : "Naimbag a malem",
            "name bug Amalie" : "Naimbag a malem",
            "Name by Eminem" : "Naimbag a malem",
            "lamborgh": "naimbag a malem",
            "I'm back": "naimbag a malem",
            "lamborghin": "naimbag a malem",
            "lady bug on my": "naimbag a malem",
            "bug": "naimbag a malem",
            "name bug Amal": "naimbag a malem",
            "nothing but a mile": "naimbag a malem",
            "nothing bug": "naimbag a malem",
            "naimbag a malem on my": "naimbag a malem",
            "naimbag a malem on my Lim": "naimbag a malem",
            "nambag a malem": "naimbag a malem",
            "iron bag a malem": "naimbag a malem", 
            "nambag malim": "naimbag a malem",
            "iron bag malim": "naimbag a malem",
            "my bag malem": "naimbag a malem",
            "name bug em": "naimbag a malem",
            "nothing bug a": "naimbag a malem",
            "laying bug on": "naimbag a malem",
            "name bug Amazon": "naimbag a malem",
            "name naimbag a malem": "naimbag a malem",

            "Name by Eminem" : "Naimbag a rabii",
            "name bug are" : "Naimbag a rabii",
            "9 bug Arab" : "Naimbag a rabii",
            "9 bug are" : "Naimbag a rabii",
            "play Bad are" : "Naimbag a rabii",
            "9 bag are" : "Naimbag a rabii",
            "my inbox Arabic" : "Naimbag a rabii",
            "name bag Arabic" : "Naimbag a rabii",
            "Play Arab" : "Naimbag a rabii",
            "nothing but Arabic" : "Naimbag a rabii",
            "nightmare" : "Naimbag a rabii",
            "nothing but Arab" : "Naimbag a rabii",
            "my inbox are" : "Naimbag a rabii",
            "Nothing bug arab": "naimbag a rabii",
            "arab": "naimbag a rabii", 
            "ladybug arab": "naimbag a rabii",
            "I'm back arab": "naimbag a rabii",
            "nothing bug": "naimbag a rabii",
            "name bug naimbag a rabii": "naimbag a rabii",
            "nambag arabii": "naimbag a rabii",
            "iron bag rabii": "naimbag a rabii",
            "name bag rabii": "naimbag a rabii",
            "iron bag rabbi": "naimbag a rabii",
            "my bag rabbi": "naimbag a rabii",
            "name bug AR": "naimbag a rabii",
            "name bug Arab": "naimbag a rabii",
            "I'm back Arab": "naimbag a rabii",
        },
    }

    if language in corrections:
        for incorrect, correct in corrections[language].items():
            # Use regex for word-based replacement
            text = re.sub(rf'\b{re.escape(incorrect)}\b', correct, text, flags=re.IGNORECASE)
    return text

def recognize_speech(source_lang, target_lang):
    """Recognize speech from microphone and translate it."""
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        # Recognize speech
        recognized_text = recognizer.recognize_google(audio, language=source_lang)
        print(f"Raw Recognized ({source_lang}): {recognized_text}")

        # Normalize the transcription for the selected source language
        normalized_text = normalize_transcription(recognized_text, source_lang)
        print(f"Normalized ({source_lang}): {normalized_text}")

        # Translate normalized text
        translated_text = translate_text(normalized_text, source_lang, target_lang)
        print(f"Translated ({target_lang}): {translated_text}")

        return normalized_text, translated_text

    except sr.UnknownValueError:
        return "", "Could not understand audio."
    except sr.RequestError as e:
        return "", f"Error with speech recognition service: {e}"
    except Exception as e:
        return "", f"Error: {e}"

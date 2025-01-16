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
            password="Password",  
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
            "Mario Gabby" : "maayong gabi",
            "miami" : "maayong gabi",
            
            "maayong happen": "maayong hapon",
            "may I don't happen": "maayong hapon",
            "I don't happen": "maayong hapon",
            "my iron happen": "maayong hapon",
            "my own happened": "maayong hapon",
            "my own happen": "maayong hapon",
            "Malayalam happened" : "maayong hapon",
            "my own husband" : "maayong hapon",

            "my iron bunting": "Maayong buntag",
            "Malayalam buntag": "Maayong buntag",
            "my iron buntag": "Maayong buntag",
            "my ion buntag": "Maayong buntag",
            "Mayan buntag": "Maayong buntag",
            "my own buntag": "Maayong buntag",
            "my young buntag" : "Maayong buntag",
            "my own bunting" : "Maayong buntag",
            
            "dog hung salamat": "Daghang salamat",
            "dog Haus salamat": "Daghang salamat",
            "the gang salamat": "Daghang salamat",
            "Doug hung salamat": "Daghang salamat",
            "Doug Hahn salamat": "Daghang salamat",
            "the Khan salamat": "Daghang salamat",
            "Dog House salamat": "Daghang salamat",
            "Doug ham salamat": "Daghang salamat",
#===============================================            
            "pwede kunimoto baingan": "Pwede ko nimo tabangan?",
            "puede kunimoto baingan": "Pwede ko nimo tabangan?",
            "play the kanamoto baingan": "Pwede ko nimo tabangan?",
#===============================================  
            "baingan": "tabangan",
            "the Batman": "tabangan",
            "cabangon": "tabangan",
            
            "delete": "Dili",
            
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




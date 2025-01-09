import speech_recognition as sr
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
        print(f"Recognized ({source_lang}): {recognized_text}")

        # Translate recognized text
        translated_text = translate_text(recognized_text, source_lang, target_lang)
        print(f"Translated ({target_lang}): {translated_text}")

        return recognized_text, translated_text

    except sr.UnknownValueError:
        return "", "Could not understand audio."
    except sr.RequestError as e:
        return "", f"Error with speech recognition service: {e}"
    except Exception as e:
        return "", f"Error: {e}"

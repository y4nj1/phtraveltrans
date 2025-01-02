import speech_recognition as sr
from googletrans import Translator

# Initialize recognizer
recognizer = sr.Recognizer()
translator = Translator()

language_code_map = {
    "English": "en",
    "Tagalog": "tl",
    "Cebuano": "ceb",
    "Ilocano": "ilo"
}

# Dictionaries for manual translations
translation_dict = {
    ('en', 'tl'): {
        "hello": "kamusta",
        "goodbye": "paalam",
        "thank you": "salamat",
        "yes": "oo",
        "no": "hindi",
    },
    ('tl', 'en'): {
        "kamusta": "hello",
        "paalam": "goodbye",
        "salamat": "thank you",
        "oo": "yes",
        "hindi": "no",
    },
    ('en', 'ceb'): {
        "hello": "kumusta",
        "goodbye": "babay",
        "thank you": "salamat",
        "yes": "oo",
        "no": "dili",
    },
    ('ceb', 'en'): {
        "kumusta": "hello",
        "babay": "goodbye",
        "salamat": "thank you",
        "oo": "yes",
        "dili": "no",
    },
    ('en', 'ilo'): {
        "hello": "nagkamusta",
        "goodbye": "agyamanak",
        "thank you": "agyaman",
        "yes": "wen",
        "no": "saan",
    },
    ('ilo', 'en'): {
        "nagkamusta": "hello",
        "agyamanak": "goodbye",
        "agyaman": "thank you",
        "wen": "yes",
        "saan": "no",
    },
    ('tl', 'ceb'): {
        "salamat": "salamat",
        "oo": "oo",
        "hindi": "dili",
        "kamusta": "kumusta",
    },
    ('ceb', 'tl'): {
        "salamat": "salamat",
        "oo": "oo",
        "dili": "hindi",
        "kumusta": "kamusta",
    },
    ('tl', 'ilo'): {
        "salamat": "agyaman",
        "kamusta": "nagkamusta",
        "hindi": "saan",
        "oo": "wen",
    },
    ('ilo', 'tl'): {
        "agyaman": "salamat",
        "nagkamusta": "kamusta",
        "saan": "hindi",
        "wen": "oo",
    },
    ('ceb', 'ilo'): {
        "salamat": "agyaman",
        "kumusta": "nagkamusta",
        "dili": "saan",
        "oo": "wen",
    },
    ('ilo', 'ceb'): {
        "agyaman": "salamat",
        "nagkamusta": "kumusta",
        "saan": "dili",
        "wen": "oo",
    },
}

def manual_translate(text, src, dest):
    """Manually translate text using predefined dictionaries."""
    return translation_dict.get((src, dest), {}).get(text.lower(), text)

def translate_text(source_text, source_lang, target_lang):
    """Translate text between selected languages."""
    if (source_lang, target_lang) in translation_dict:
        # Use manual translation for predefined language pairs
        return manual_translate(source_text, source_lang, target_lang)
    else:
        # Use Google Translate API for other translations
        translated = translator.translate(source_text, src=source_lang, dest=target_lang)
        return translated.text

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

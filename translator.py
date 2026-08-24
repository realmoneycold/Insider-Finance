from deep_translator import GoogleTranslator
import os

def translate_text(text: str, target_lang: str) -> str:
    """Translates text to the target language. 'en' skips translation."""
    if target_lang == "en":
        return text
    try:
        # Google Translate can sometimes choke on heavy formatting or return Error 500 HTML
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        if not translated or "Error 500" in translated or "That’s an error" in translated:
            print(f"Google Translate returned an error string for {target_lang}")
            return text
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text

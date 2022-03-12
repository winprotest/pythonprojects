#!/usr/bin/python
#pip install google-cloud-translate==2.0.1
#pip install --upgrade google-cloud-translate
#python cloudtranslate.py
#ref : https://cloud.google.com/translate/docs/setup
#ref : https://cloud.google.com/translate/docs/basic/translating-text

import sys
import os
def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print(u"Text: {}".format(result["input"]))
    print(u"Translation: {}".format(result["translatedText"]))
    print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))


def main(argv):
    credential_path = "E:\py\googletranslation\cloud\yourauthkey.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    translate_text("de", "how are you?")

if __name__ == "__main__":
    main(sys.argv[1:])

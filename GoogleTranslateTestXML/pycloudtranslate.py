#!/usr/bin/python
"""
Author : Win
This file can be used to translate string using Google Cloud API.
You will need to have the API key json file. Read more at : https://cloud.google.com/iam/docs/creating-managing-service-account-keys
This is used together with pytranslate.py to get the translated string using Cloud API if the googletrans translation fails to translate.
This is the back up method for translation if googletrans method fails.
"""
#pip install google-cloud-translate==2.0.1
#pip install --upgrade google-cloud-translate
#python cloudtranslate.py
#ref : https://cloud.google.com/translate/docs/setup
#ref : https://cloud.google.com/translate/docs/basic/translating-text

import sys
import os
import argparse

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
    try:
        result = translate_client.translate(text, target_language=target)
        if result:
            print(u"Text: {}".format(result["input"]))
            print(u"Translation: {}".format(result["translatedText"]))
            print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
        else:
            print("FAIL CLOUD TRANSLATION!")
    except Exception as error:
        print(error)

    return result


#This is the default API Key Path. If you do not want to provide keypath everytime this program is called,
#you can set the default key Path here and this client will get it from here everytime this program is called.
def setDefaultConfigureAPIKeyPath():
    from os.path import exists
    DEFAULT_API_KEY_PATH = ("D:\\GitHub\\DefaultConfig\\myproject.json")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = DEFAULT_API_KEY_PATH
    fileexist = exists(DEFAULT_API_KEY_PATH)
    print("Set default API Key Path:"+str(DEFAULT_API_KEY_PATH) + " exist:"+str(fileexist))
    return fileexist

def configureCloudAPIKeyPath(keypath):
    credential_path = keypath
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    print("Set cloud API Key Path:"+str(keypath))

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--text',type=None, default= "", help="Text string to translate.",required=False)
    parser.add_argument("-k","--keypath", type=None, default= "",help="Set cloud API Key Path.",required=False)
    parser.add_argument("-l", "--lan", type=None, default= "",help="Destination Language to translate to.",required=False)

    args = parser.parse_args(args)
    #print("## CLOUD ### args:"+str(args))
    if args.text and args.lan:
        if (args.keypath):
            configureCloudAPIKeyPath(args.keypath)
        else:
            setDefaultConfigureAPIKeyPath()
        
        print(args)
        try:
            translatedtext = translate_text(args.lan, args.text)
            print(translatedtext)
            if translatedtext:
                return translatedtext["translatedText"]
        except Exception as error:
            print(error)

    elif args.keypath:
        configureCloudAPIKeyPath(args.keypath)
    else:
        print("No valid language or text to translate.")

    #test code
    #translate_text("it", "Scheduled") #Programmato
    #translate_text("it", "Favourites") #Preferiti


if __name__ == "__main__":
    main(sys.argv[1:])
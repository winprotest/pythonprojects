#!/usr/bin/python
"""
Author : Win
This file can be used to create translated string xml file from English string xml.
Suggestion : to upload only small difference file instead of using the whole file for translation as the larger the file is the longer it takes for translation.
"""
#to run this you need googletrans==4.0.0rc1 and Pandas packages
#and may need numpy package

#install necessary packages
#!pip install googletrans==4.0.0rc1
#!pip install pandas
#!pip install numpy

import sys, getopt
import io
    
def chekValidLanguage(lan):
    import googletrans
    from googletrans import Translator

    translator = Translator()
    avaialable = googletrans.LANGUAGES
    lanValue = avaialable.get(lan)
    print(lanValue)
    return False if (lanValue is None) else True 

def convertToDict(filename):
    import xml.etree.ElementTree as ET
    xml_data = open(filename, 'r').read()  # Read file
    root = ET.XML(xml_data)  # Parse XML

    xmld = {x.text:x.attrib['name'] for x in root.findall('string') if x.text}
    kvdict =  {value : key for (key, value) in xmld.items()}

    #cleanse strings in dict
    kvdict = {key:vl for key, vl in kvdict.items() if '&lt;' not in vl and vl.startswith('\\u') == False and vl.startswith('***') == False}
    kvdict = {key:vl for key, vl in kvdict.items() if vl.startswith('|') == False and vl.startswith('https://') == False}
    kvdict = {key:vl.replace("\"","") for key, vl in kvdict.items() if key != 'about_legal_notices' and key != 'android_intent_extra_stream'}
    return kvdict

def getTranslatedDF(d, lan):
    import pandas as pd
    import googletrans
    from googletrans import Translator

    #translate for the dest languague and create dest dict
    #this may take time doing translation if the original file is big.
    translator = Translator()
    destDict ={}
    neworiginalDict ={}
    for k,v in d.items():
        try:
            translated = translator.translate(v, dest=lan)
            destDict[k]= translated.text
            neworiginalDict[k] = v
        except Exception as error:
            print('Exception translated key:'+k + " value:"+v + " error:"+error)

    #create language dataframe from source 'English' first
    translationdf =pd.DataFrame.from_dict(neworiginalDict, orient='index')

    #add dest string into the original df
    translationdf[lan] = destDict.values()   
    return translationdf

def covertTranslatedDataFrameToXML(df, destLanguage, translatedFileName):
    import xml.dom.minidom as minidom
    import xml.etree.ElementTree as ET
    
    root = ET.Element("resources")
    for index, row in df.iterrows():
        mitem = row[destLanguage]
        ET.SubElement(root, "string", name=index).text = mitem
    
    tree = ET.ElementTree(root)    
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    #print it out the translated xml
    print("This is the translated strings resource xml.")
    print(xmlstr)

    #if file name is not null, save into file.
    if translatedFileName:
        print("File name:"+translatedFileName + " is created.")
        with open(translatedFileName, "w", encoding="utf-8") as f:
            f.write(xmlstr)

        
def main(argv):
    inputXMLfile = ''
    destinationLanguage = ''
    try:
        opts, args = getopt.getopt(argv,"hf:l:",["inputXMLfile=","destinationLanguage="])
    except getopt.GetoptError:
        print('googletranslate_xmlconvert.py -f <inputXMLfile> -l <destinationLanguage>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('googletranslate_xmlconvert.py -f <inputXMLfile> -l <destinationLanguage>')
            sys.exit()
        elif opt in ("-f", "--inputXMLfile"):
            inputXMLfile = arg
        elif opt in ("-l", "--destinationLanguage"):
            destinationLanguage = arg
    print('Input XML file is ', inputXMLfile)
    print('Destination Language is ', destinationLanguage)
    if inputXMLfile and destinationLanguage:
        validlan = chekValidLanguage(destinationLanguage)
        if validlan:
            d = convertToDict(inputXMLfile)
            print(len(d))
            if len(d) > 0:
                df = getTranslatedDF(d,destinationLanguage)
                if df.size > 0:
                    translatedfileName = inputXMLfile + "_" +destinationLanguage +".xml"
                    covertTranslatedDataFrameToXML(df, destinationLanguage, translatedfileName)
        else:
            print("ERROR: Invalid destination language." + destinationLanguage + " is not supported.")
    else:
        print("ERROR: Invalid input or destination language.")
        

if __name__ == "__main__":
   main(sys.argv[1:])



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
#!pip install lxml

import sys, getopt
import io
import json
import os
import googletrans

def chekValidLanguage(lan):
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
    from googletrans import Translator

    #translate for the dest languague and create dest dict
    #this may take time doing translation if the original file is big.
    translator = Translator()
    destDict ={}
    neworiginalDict ={}
    notranslatedDict = {}
    print('Start translating for :'+lan)
    for k,v in d.items():
        if k and v:
            print('Please wait...Translating now for:'+k + " v:"+v)
            try:
                totranslate = v.replace(":" , " ")
                translated = translator.translate(totranslate, dest=lan)
                if translated:
                    destDict[k]= translated.text
                    neworiginalDict[k] = v
            except Exception as error:
                notranslatedDict[k]=v
                print('Exception translated key:'+k + " value:"+v)

    #create language dataframe from source 'English' first
    translationdf =pd.DataFrame.from_dict(neworiginalDict, orient='index')

    #add dest string into the original df
    translationdf[lan] = destDict.values()   
    return translationdf,notranslatedDict

def getTranslatedDict(d, lan):
    from googletrans import Translator

    #translate for the dest languague and create dest dict
    #this may take time doing translation if the original file is big.
    translator = Translator()
    destDict ={}
    neworiginalDict ={}
    notranslatedDict = {}
    print('Start translating for :'+lan)
    for k,v in d.items():
        if k and v:
            print('Please wait...Translating now for:'+k + " v:"+v)
            try:
                totranslate = v.replace(":" , " ")
                translated = translator.translate(totranslate, dest=lan)
                if translated:
                    destDict[k]= translated.text
                    neworiginalDict[k] = v
            except Exception as error:
                notranslatedDict[k]=v
                print('Exception translated key:'+k + " value:"+v)
    
    return destDict,notranslatedDict

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

def parseIOSXLIFF(filename):
    import lxml
    from lxml import etree

    tree = etree.iterparse(filename)
    dkey = ""
    dvalue = ""
    iosDict= {}
    for action,elem in tree:
        if 'source' in elem.tag:
            dkey = elem.text
        if 'target' in elem.tag:
            dvalue = elem.text
        if dkey and dvalue:
               iosDict[dkey] = dvalue
               print("dkey: " + dkey + " dvalue:"+ dvalue)
               dkey = ""
               dvalue =""        
    return iosDict

def saveTranslatedToXLIFF(oFileName, tFileName, tDict):
    import lxml
    from lxml import etree
    import xml.etree.ElementTree as ET

    tree = etree.iterparse(oFileName)
    dkey = ""
    for action,elem in tree:
        if 'source' in elem.tag:
            dkey = elem.text
        if 'target' in elem.tag:
            elem.text = tDict[dkey]
            dkey = ""
    
    print("Write translated strings to a new file "+ tFileName)
    root = tree.root
    #print(etree.tostring(root)) #print xliff string
    with open(tFileName, 'wb') as f:
        f.write(etree.tostring(root,encoding="utf-8",pretty_print=True,xml_declaration = True))


def main(argv):
    inputFile = ''
    destinationLanguage = ''
    try:
        opts, args = getopt.getopt(argv,"hf:l:",["inputFile=","destinationLanguage="])
        pyfilename = os.path.basename(sys.argv[0])
        print("Python file name %s"%pyfilename)
    except getopt.GetoptError:
        print('%s -f <inputFile> -l <destinationLanguage>'%pyfilename)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Command:' )
            print('%s -f <inputFile> -l <destinationLanguage>'%pyfilename)
            print('Available languages:' )                        
            print(googletrans.LANGUAGES)
            sys.exit()
        elif opt in ("-f", "--inputFile"):
            inputFile = arg
        elif opt in ("-l", "--destinationLanguage"):
            destinationLanguage = arg
    print('Input file is ', inputFile)
    print('Destination Language is ', destinationLanguage)
    if inputFile and destinationLanguage and inputFile.endswith(".xml"):
        validlan = chekValidLanguage(destinationLanguage)
        if validlan:
            d = convertToDict(inputFile)           
            if d and len(d) > 0:
                print("Total strings to translate %s" % (len(d)))
                df, errorDict = getTranslatedDF(d,destinationLanguage)
                if df.notnull and df.size > 0:
                    print("Total translated strings %s" % (len(df)))
                    inputfilenameOnly = os.path.splitext(inputFile)[0] #remove extension
                    translatedfileName = inputfilenameOnly + "_" +destinationLanguage +".xml"
                    covertTranslatedDataFrameToXML(df, destinationLanguage, translatedfileName)
                    if errorDict and len(errorDict) > 0:
                        with open(inputfilenameOnly + "_" +destinationLanguage + "_nottranslated" + '.txt', 'w') as file:
                             file.write(json.dumps(errorDict))
                else:
                    print("ERROR Fail translation for this "+destinationLanguage)
    elif inputFile and destinationLanguage and inputFile.endswith(".xliff"):
        validlan = chekValidLanguage(destinationLanguage)
        if validlan:
            print("iOS File")
            d = parseIOSXLIFF(inputFile)
            if d and len(d) > 0:
                print("Total strings to translate %s" % (len(d)))
                translatedDict, errorDict = getTranslatedDict(d,destinationLanguage)
                if translatedDict and len(translatedDict) > 0:
                    print("Total translated strings %s" % (len(translatedDict)))
                    inputfilenameOnly = os.path.splitext(inputFile)[0] #remove extension
                    translatedfileName = inputfilenameOnly + "_" +destinationLanguage +".xliff"
                    saveTranslatedToXLIFF(inputFile, translatedfileName, translatedDict)
        else:
            print("ERROR: Invalid destination language." + destinationLanguage + " is not supported.")
    else:
        print("ERROR: Invalid input or destination language.")
        

if __name__ == "__main__":
   main(sys.argv[1:])



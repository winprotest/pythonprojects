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
#!pip install lxml

"""
 Example Usage:
	pytranslate.py -i inputfilename -l destinationlanguage
	pytranslate.py -i inputfilename -o outputfilename -l destinationlanguage
	pytranslate.py -h
	E.g. 
	Translate the input file "test.json" to  German/de and overwrite the input file "test.json".
	pytranslate.py -i "test.json" -l "de"

	Translate the input file "en.json" to German/de language and put the result in "de.json" file.
	pytranslate.py -i "en.json" -o "de.json" -l "de"

	Translate the input file "testxml.xml" to Slovak language and put the result in "test_sv." file.
	pytranslate.py -i "testxml.xml" -l "sv" -o "test_sv.xml"

	usage: pytranslate.py [-h] -i INPUT [-o OUTPUT] -l LAN

	options:
	  -h, --help            show this help message and exit
	  -i INPUT, --input INPUT
							Input file name to translate.
	  -o OUTPUT, --output OUTPUT
							Output file name to write the translated strings.
	  -l LAN, --lan LAN     Destination Language to translate to.
"""

import string
import sys
import io
import json
import os
import googletrans
import lxml
import argparse
import chardet

class ValidityCheck():
    import googletrans as gtrans
    def __init__(self):
        self.listExtensions = ['.xml','.xliff','.properties', '.json', '.strings']

    def isValidForTranslation(self, inputfilename, lan):
        validExtension = self.isValidExtension(inputfilename)
        validLan = self.isValidLanguage(lan)
        return validExtension and validLan

    def isValidExtension(self, inputfilename):
        print("Is this valid file? ", inputfilename )
        if inputfilename:
            filename, file_extension = os.path.splitext(inputfilename)
            if file_extension and file_extension in self.listExtensions:
                return True
        return False

    def isValidLanguage(self, lan):
        print("Is this valid Language? ", lan )
        avaialable = self.gtrans.LANGUAGES
        lanValue = avaialable.get(lan)
        return False if (lanValue is None) else True
    
    def getValidLanguages(self):
        return  self.gtrans.LANGUAGES

def convertToDict(filename):
    import xml.etree.ElementTree as ET
    detectEncoding = 'utf-8'
   
    with open(filename, 'rb') as file:
        raw = file.read(32) # at most 32 bytes are returned
        detectEncoding = chardet.detect(raw)['encoding']
        print(detectEncoding)

    if detectEncoding == 'ascii':
         detectEncoding = 'utf-8'
    xml_data = open(filename, 'r', encoding=detectEncoding).read()  # Read file
    root = ET.XML(xml_data)  # Parse XML

    xmld = {x.text:x.attrib['name'] for x in root.findall('string') if x.text}
    kvdict =  {value : key for (key, value) in xmld.items()}

    #cleanse strings in dict
    kvdict = {key:vl for key, vl in kvdict.items() if '&lt;' not in vl and vl.startswith('\\u') == False and vl.startswith('***') == False}
    kvdict = {key:vl for key, vl in kvdict.items() if vl.startswith('|') == False and vl.startswith('https://') == False}
    
    return kvdict

def getTranslatedDF(d, lan):
    import pandas as pd
    from googletrans import Translator
    import pycloudtranslate as pc

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
                #this is for handling of %1$d %1$s etc
                #according to web, strings like this will not translate __1__ 
                totranslate = v 
                listvariables = [word for word in v.split() if (word.startswith('%') and word.contains("$")) or (word == ":")]
                #print(listvariables)
                for i, vr in enumerate(listvariables):                   
                    totranslate = totranslate.replace(str(vr),"__"+str(i)+"__")

                #print("totranslate:"+str(totranslate))
                tv =""
                try:
                    translated = translator.translate(totranslate, dest=lan)
                except Exception as translateerror:
                    print(translateerror)
                    translated =""
                if not translated:
                    tv = pc.main(["-t",totranslate, "-l",lan])                    

                if translated or tv:
                    if type(translated) is googletrans.models.Translated:                        
                        tv =translated.text    
                                       
                    if not tv:
                        notranslatedDict[k]=v                        
                        continue

                    if listvariables:
                        for i, vr in enumerate(listvariables):                   
                            tv = tv.replace("__"+str(i)+"__",vr)
                    destDict[k] = tv
                    neworiginalDict[k] = v
                else:
                    notranslatedDict[k]=v                        
                    continue                                       
            except Exception as error:
                notranslatedDict[k]=v
                print(error)
                print('Exception translated key:'+k + " value:"+v)

    #create language dataframe from source 'English' first
    translationdf =pd.DataFrame.from_dict(neworiginalDict, orient='index')

    #add dest string into the original df
    translationdf[lan] = destDict.values()
    return translationdf,notranslatedDict

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
        with open(translatedFileName, "w", encoding="utf-8") as f:
            f.write(xmlstr)            
        print("Write translated strings to a new file "+ translatedFileName)
        print("---------------------------save To %s ---------------------------------"%(str(translatedFileName)))

#for iOS specific as this will translate key
#we will translate the key/source and put as target
def getTranslatedDict(d, lan):
    from googletrans import Translator
    import pycloudtranslate as pc
    #translate for the dest languague and create dest dict
    #this may take time doing translation if the original file is big.
    translator = Translator()
    destDict ={}
    notranslatedDict = {}
    print('Start translating for :'+lan)
    for k,v in d.items():
        if k:
            print('Please wait...Translating now for:'+k + " v is Empty:"+v)
            try:
                totranslate = k
                listvariables = [word for word in k.split() if (word.startswith('%@') or word.startswith('%d'))]
                #print(listvariables)
                for i, vr in enumerate(listvariables):         
                    totranslate = totranslate.replace(str(vr),"__"+str(i)+"__")
                
                tv=""
                try:
                    translated = translator.translate(totranslate, dest=lan)
                except Exception as translateerror:
                    print(translateerror)
                    translated =""
                if not translated:
                    tv = pc.main(["-t",totranslate, "-l",lan])
                    #print("############# A CLOUD totranslate:"+str(totranslate) + " translated:"+str(translated))

                if translated or tv:
                    if type(translated) is googletrans.models.Translated:                        
                        tv =translated.text

                    if not tv:
                        notranslatedDict[k]=v                        
                        continue                        
                    
                    if listvariables:
                        for i, vr in enumerate(listvariables):                   
                            tv = tv.replace("__"+str(i)+"__",vr)

                    destDict[k]= tv
                else:
                    notranslatedDict[k]=v                        
                    continue
            except Exception as error:
                notranslatedDict[k]=v
                print(error)
                print('Exception translated key:'+k + " value:"+v)
    
    return destDict,notranslatedDict

#for iOS specific    
def parseIOSXLIFF(filename):
    from lxml import etree

    skipkeys =['XXXXXXXXXXX','00:00:00','0:00','1','30','12','10','1']

    tree = etree.iterparse(filename)
    dkey = ""
    dvalue = ""
    iosDict= {}
    for action,elem in tree:
        if 'source' in elem.tag:
            dkey =""
            if elem.text.lower() in skipkeys:
                print('skip key for this:'+elem.text)
                continue
                    
            dkey = elem.text
            dvalue = ""
        if 'target' in elem.tag:            
            if dkey and dkey == elem.text:
                dvalue = ""
                print('SAME: dkey:'+dkey + " elem.text:"+ elem.text)
            else:
                dvalue = elem.text
        if 'note' in elem.tag: #when we are here, and dvalue is empty meaning this needs to translate
            if 'Do not translate'.lower() in elem.text.lower():
                print('skip donottranslate key for this:'+elem.text)                
                continue               
            if dkey and not dvalue:
                iosDict[dkey] = dvalue
                print("Strings to translate dkey: " + dkey + " dvalue:"+ dvalue)
                dkey = ""
                dvalue =""

    return iosDict

#for iOS specific
def saveTranslatedToXLIFF(oFileName, tFileName, tDict):    
    from lxml import etree

    #print(json.dumps(tDict))
    tree = etree.iterparse(oFileName)
    transunitRoot = None
    dkey = ""
    for action,elem in tree:
        if 'trans-unit' in elem.tag:
            transunitRoot = elem
            dkey =""
            listele = list(transunitRoot)
            if listele:
                #assuming trans-uint has source,target, note
                removeCurrentTarget = False       
                for c in elem:
                    if 'source' in c.tag:
                        dkey =  c.text
                        if dkey in tDict:
                            if len(listele) > 2:
                                removeCurrentTarget = True #we are going to replace with new one so remove current one
                                print("add this new key:"+dkey + " value:"+tDict[dkey])
                            target = etree.SubElement(transunitRoot, "target")
                            target.text = tDict[dkey]
                            target.tail = '\n'
                            #print("to insert target key:"+dkey + " value:"+tDict[dkey])
                            elem.insert(1,target)
                    if 'target' in c.tag and removeCurrentTarget:
                        print("remove this old key:"+dkey + " value:"+c.tag)
                        transunitRoot.remove(c)

    
    print("Write translated strings to a new file "+ tFileName)
    print("---------------------------save To %s---------------------------------"%(str(tFileName)))
    root = tree.root
    etree.indent(root, space="    ")
   #print(etree.tostring(root)) #print xliff string
    with open(tFileName, 'wb') as f:
        f.write(etree.tostring(root,encoding="utf-8",pretty_print=True,xml_declaration = True))


#for java properties files
def parsePropertiesStrings(filename):
    d = {}   
    detectEncoding = 'utf-8'
   
    with open(filename, 'rb') as file:
        raw = file.read(32) # at most 32 bytes are returned
        detectEncoding = chardet.detect(raw)['encoding']
        print(detectEncoding)
    if detectEncoding == 'ascii':
         detectEncoding = 'utf-8'
    with open(filename, encoding=detectEncoding) as f:
        d = dict(line.rstrip().split("=", 1) for line in f if line and not line.startswith("#") and "=" in line )
        if filename.endswith(".strings"):
            d.update((k, str(v).replace(";","").replace("\"","")) for k,v in d.items())
    print(json.dumps(d))
    return d

#for properties and json files. as we want to translate value of this one and then replace with the newly translated one
#can probably keep same function and do differently for ios and properties but better to have their own for more flexibility
#input : contacts_title = Contacts
#output : contacts_title = Kontakt
def getTranslation(d, lan):
    from googletrans import Translator
    import pycloudtranslate as pc
    #translate for the dest languague and create dest dict
    #this may take time doing translation if the original file is big.
    translator = Translator()
    destDict ={}
    notranslatedDict = {}
    print('Start translating for :'+lan)
    for k,v in d.items():
        if k:
            print('Please wait...Translating now for:'+k + " v is Empty:"+v)
            try:
                totranslate = v
                listvariables = [word for word in v.split() if (word.startswith('%@') or word.startswith('%d'))]
                #print(listvariables)
                for i, vr in enumerate(listvariables):   
                    totranslate = totranslate.replace(str(vr),"__"+str(i)+"__")
                
                tv=""
                try:
                    translated = translator.translate(totranslate, dest=lan)
                except Exception as translateerror:
                    print(translateerror)
                    translated =""
                if not translated:
                    tv = pc.main(["-t",totranslate, "-l",lan])
        
                if translated or tv:
                    if type(translated) is googletrans.models.Translated:                        
                        tv =translated.text    
                    
                    if not tv:
                        notranslatedDict[k]=v                        
                        continue

                    if listvariables:
                        for i, vr in enumerate(listvariables):                   
                            tv = tv.replace("__"+str(i)+"__",vr)

                    destDict[k]= tv
                else:
                    notranslatedDict[k]=v                        
                    continue                                        
            except Exception as error:
                notranslatedDict[k]=v
                print(error)
                print('Exception translated key:'+k + " value:"+v)
    
    return destDict,notranslatedDict

def savePropertiesStrings(d, oFileName):    
    if d and oFileName:
        startquote = ""
        endquote =""
        if oFileName.endswith(".strings"):
            startquote ="\""
            endquote = "\";"
        
        kv = [(k + " = " + startquote + v +endquote) for k,v in d.items()]
        tdstr = "\n".join(kv)
        print(tdstr)
        with open(oFileName, "w", encoding="utf-8") as f:
            f.write(tdstr)
        
        print("Write translated strings to a new file "+ oFileName)
        print("---------------------------save To %s---------------------------------"%(str(oFileName)))

def parseJSON(fileName):
    d ={}
    detectEncoding = 'utf-8'
   
    with open(fileName, 'rb') as file:
        raw = file.read(32) # at most 32 bytes are returned
        detectEncoding = chardet.detect(raw)['encoding']
        print(detectEncoding)
    if detectEncoding == 'ascii':
         detectEncoding = 'utf-8'
    with open(fileName,'r',encoding=detectEncoding) as f:
        d = json.load(f)

    #print(json.dumps(d))
    return d

def saveJSON(d, oFileName):
    if d and oFileName:     
        with open(oFileName,'w',encoding="utf-8") as f:
            #indent2 for new line, ascii=false for unicode
            json.dump(d, f,indent=2,ensure_ascii=False)   
        print("Write translated strings to a new file "+ oFileName)
        print("---------------------------save To %s---------------------------------"%(str(oFileName)))


def main(args):
    print(args)
    pyfilename = ""
    inputFile = ''
    outputFile = ""
    destinationLanguage = ''
    translatedfileName = ""
    try:      
        pyfilename = os.path.basename(sys.argv[0])
        print("Python file name %s"%pyfilename)
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input',type=None, default= "", help="Input file name to translate.",required=True)
        parser.add_argument("-o","--output", type=None, default= "",help="Output file name to write the translated strings.",required=False)
        parser.add_argument("-l", "--lan", type=None, default= "",help="Destination Language to translate to.",required=True)
        args = parser.parse_args(args)
        print(args)
    except Exception as e:
        print(e)
        #print('%s -i <inputFile> -o <outputFile> -l <destinationLanguage>'%pyfilename)
        sys.exit(2)

    inputFile = args.input
    outputFile =args.output
    destinationLanguage = args.lan
    translatedfileName = ""
    proceed = True
    print('Input file is ', inputFile)
    if outputFile:
        print('Output file is ',outputFile)
    else:
        print('Output file name is not specified. So input file will be overwritten.')

    print('Destination Language is ', destinationLanguage)
    
    validity = ValidityCheck()
    if inputFile and destinationLanguage:
        proceed = validity.isValidForTranslation(inputFile, destinationLanguage)               
    else:
        print('Provide valid file and destination language to translate.')
        proceed = False
 
    inputfilenameOnly, inputextension = os.path.splitext(inputFile)

    if outputFile:
        outputfilenameOnly, outputextension = os.path.splitext(outputFile)
        if (outputextension != inputextension):
            print("Output File extension must be the same as Input File extension.")
            proceed = False
        else:
            translatedfileName = outputFile
    else:
        translatedfileName = inputFile #overwrite the input file

    if not proceed:
        print('Cannot proceed for translation...')
        sys.exit()

    print("Translate the inputfile:" + str(inputFile) + " for this language:"+str(destinationLanguage) +"")  
    #everything looks fine, go ahead with Translation        
    if inputFile.endswith(".xml"):
        d = convertToDict(inputFile)           
        if d and len(d) > 0:
            print("Total strings to translate %s" % (len(d)))
            df, errorDict = getTranslatedDF(d,destinationLanguage)
            if df.notnull and df.size > 0:
                print("Total translated strings %s" % (len(df)))                                     
                covertTranslatedDataFrameToXML(df, destinationLanguage, translatedfileName)
            if errorDict and len(errorDict) > 0:
                nottranslatedfile = inputfilenameOnly + "_" +destinationLanguage + "_nottranslated" + '.txt'
                with open(nottranslatedfile, 'w') as file:
                        file.write(json.dumps(errorDict))
                        print(nottranslatedfile + " is created."+ "Total not translated strings %s" % (len(errorDict)))
        else:
            print("ERROR Fail translation for this "+destinationLanguage)
    elif inputFile.endswith(".xliff"):      
        print("iOS File")
        d = parseIOSXLIFF(inputFile)
        if d and len(d) > 0:
            print("Total strings to translate %s" % (len(d)))
            translatedDict, errorDict = getTranslatedDict(d,destinationLanguage)
            if translatedDict and len(translatedDict) > 0:
                print("Total translated strings %s" % (len(translatedDict)))
                #print(json.dumps(translatedDict))
                saveTranslatedToXLIFF(inputFile, translatedfileName, translatedDict)
            if errorDict and len(errorDict) > 0:
                nottranslatedfile = inputfilenameOnly + "_" +destinationLanguage + "_nottranslated" + '.txt'
                with open(nottranslatedfile, 'w') as file:
                        file.write(json.dumps(errorDict))
                        print(nottranslatedfile + " is created."+ "Total not translated strings %s" % (len(errorDict)))
        else:
            print("ERROR Fail translation for this "+destinationLanguage)

    elif inputFile.endswith(".properties") or inputFile.endswith(".strings"):        
        print("properties or strings File "+str(inputFile))
        d = parsePropertiesStrings(inputFile)
        if d and len(d) > 0: 
            print(json.dumps(d))
            print("Total strings to translate %s" % (len(d)))
            td, errorDict = getTranslation(d,destinationLanguage)
            if td and len(td) > 0:
                print("Total translated strings %s" % (len(td)))
                #print("Translated dict:" + json.dumps(td))
                savePropertiesStrings(td,translatedfileName)
            if errorDict and len(errorDict) > 0:
                nottranslatedfile = inputfilenameOnly + "_" +destinationLanguage + "_nottranslated" + '.txt'
                with open(nottranslatedfile, 'w') as file:
                        file.write(json.dumps(errorDict))
                        print(nottranslatedfile + " is created."+ "Total not translated strings %s" % (len(errorDict)))
            
    elif inputFile.endswith(".json"):       
        print("json File")
        d = parseJSON(inputFile)   
        if d and len(d) > 0: 
        #    print(json.dumps(d))
            print("Total strings to translate %s" % (len(d)))
            td, errorDict = getTranslation(d,destinationLanguage)
            if td and len(td) > 0:
                print("Total translated strings %s" % (len(td)))
                #print("Translated dict:" + json.dumps(td))
                saveJSON(td,translatedfileName)
            if errorDict and len(errorDict) > 0:
                nottranslatedfile = inputfilenameOnly + "_" +destinationLanguage + "_nottranslated" + '.txt'
                with open(nottranslatedfile, 'w') as file:
                        file.write(json.dumps(errorDict))
                        print(nottranslatedfile + " is created."+ "Total not translated strings %s" % (len(errorDict)))
                    
    else:
        print("ERROR: Invalid input file.")
        

if __name__ == "__main__":
   main(sys.argv[1:])

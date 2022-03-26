Read Me
==========

This was tested with Python Python 3.7.3
To run this you need googletrans==4.0.0rc1 and Pandas packages
and may need numpy package as pandas has dependency on numpy.

Install necessary packages
pip install googletrans==4.0.0rc1
pip install pandas
pip install numpy
pip install --upgrade numpy
pip install --upgrade pandas
pip install lxml

This  python file can be used to create translated string xml file from English string xml.
Suggestion is to upload only small difference file instead of using the whole file for translation as the larger the file is the longer it takes for translation.
Make sure to use only the valid English string values in xml. There are some xml cleaning is done. It may require more special cleansing of xml file.

Accepted file format : android xml string files, iOS xliff files, iOS *.strings files , *.properties files, *.json files


Android Clients
===============
The expected input xml file format is as follow for Android Clients.
<resources> 
    <string name="delete_group_confirmation">Are you sure you want to delete the selected group?</string>
</resources>

iOS Clients
================
For the expected input xliff file format for iOS clients, please check iOS_fr.xliff


Steps
=====
1. 	Put the input files and py file in the same folder.

2. 	Usage for translating individual file
	======================================
	
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
	  	  

3.  Usage for translating the whole folder
	======================================
	1. "iOSTranslated" is the folder/directory name. The files inside the "iOSTranslated" will get translated. The folder name is used as a destination language. 
		For example, this file "iOSTranslated\cs\cs.xliff" will be translated into "cs" as destination language.
	Usage:
		pyfoldertranslate.py "iOSTranslated"



4. 	If there are some error during translations, the strings that are not translated will be shown in "androidstringdiff_de_nottranslated.txt" or "iOS_fr_de_nottranslated.txt" file.

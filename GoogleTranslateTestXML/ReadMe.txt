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


Android Clients
===============
The expected input xml file format is as follow for Android Clients.
<resources> 
    <string name="delete_group_title_alert">Delete Group</string>
    <string name="delete_group_confirmation">Are you sure you want to delete the selected group?</string>
</resources>

iOS Clients
================
For the expected input xliff file format for iOS clients, please check iOS_fr.xliff


Steps
=====
1. 	Put the input files and py file in the same folder.

2. 	For example, to translate input xml file named "androidstringdiff.xml" to German/de.
	Run as below 
		pytranslate.py -f "androidstringdiff.xml" -l "de"
	 or 
		python pytranslate.py -f "androidstringdiff.xml" -l "de"
		
	For example, to translate input xliff file named "iOS_fr.xliff" to German/de.
	Run as below 
		pytranslate.py -f "iOS_fr.xliff" -l "de"
	 or 
		python pytranslate.py -f "iOS_fr.xliff" -l "de"

3. 	If it is executed successfully, the result translated output file will be generated "androidstringdiff_de.xml" or "iOS_fr_de.xliff" in the same folder.

4. 	If there are some error during translations, the strings that are not translated will be shown in "androidstringdiff_de_nottranslated.txt" or "iOS_fr_de_nottranslated.txt" file.

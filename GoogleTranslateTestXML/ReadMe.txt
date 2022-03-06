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

This  python file can be used to create translated string xml file from English string xml.
Suggestion is to upload only small difference file instead of using the whole file for translation as the larger the file is the longer it takes for translation.
Make sure to use only the valid English string values in xml. There are some xml cleaning is done. It may require more special cleansing of xml file.


The expected input xml file format is as follow:
<resources> 
    <string name="delete_group_title_alert">Delete Group</string>
    <string name="delete_group_confirmation">Are you sure you want to delete the selected group?</string>
</resources>

1. Put following input xml and py files in the same folder.

2. Run as below:
	googletranslate_xmlconvert.py -f "androidstringdiff.xml" -l "de"
 or 
	python googletranslate_xmlconvert.py -f "androidstringdiff.xml" -l "de"


3. If it is executed successfully, the result translated output file will be generated "androidstringdiff_de.xml" in the same folder.
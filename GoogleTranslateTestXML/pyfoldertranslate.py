# import required module
import sys
import os
import argparse
from pathlib import Path
import pytranslate as pt

"""
Assumption : Folder structure similar as below.
iOSTranslated\\cs\\string.xliff

here, cs is the language to translate to.
Inside folder names are based on destination language.
"""
 

def main(argv):
    #print(argv)
    validListFileExtension = ['.xml','.xliff','.properties', '.json', '.strings']
    try:      
        pyfilename = os.path.basename(sys.argv[0])
        #print("Python file name %s"%pyfilename)
        parser = argparse.ArgumentParser(str(pyfilename))
        parser.add_argument("dir", help="Input directory name to translate.")      
        args = parser.parse_args()
    except:
        sys.exit(2)
    
    
    inputDir = args.dir
    if inputDir:
        print("Input directory : "+inputDir)         
        files = Path(inputDir).glob('*')
        for dirpath, dirs, files in os.walk(inputDir):
            isFile = os.path.isfile(dirpath)
            print(str(os.path.basename(dirpath)) + " Folder:"+str(isFile))
            for f in files:
                isFile = os.path.isfile(os.path.join(dirpath,f))
                print(str(os.path.basename(f)) + " isFile2:"+str(isFile))
                if isFile:
                    filename, file_extension = os.path.splitext(f)
                    if file_extension and file_extension in validListFileExtension:
                        destlan = os.path.basename(dirpath)
                        validity = pt.ValidityCheck()
                        if validity.isValidLanguage(destlan):
                            arglist = [str(os.path.join(dirpath,f)),str(destlan)]
                            print(arglist)
                            pt.main(["-i",str(os.path.join(dirpath,f)), "-l",str(destlan)])
                           

if __name__ == "__main__":   
   main(sys.argv[1:])
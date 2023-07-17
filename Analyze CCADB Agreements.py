import glob
import pandas as pd
import csv
from pathlib import Path
from readability import Readability
import re
import os
import shutil
import time
from datetime import datetime
import multiprocessing as mp
import pytesseract
from pdf2image import convert_from_path
import string
punctuation = str.maketrans(' ',' ','!\"#$%&()*+/=@[\\\\]^{|}~')
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\Program Files\poppler-0.68.0\bin"
# https://catalog.data.gov/dataset/credit-card-agreements-database 
# download all credit cards agreement from the data gov website

def unzip_file(path): # unzip all files and remove the zipped files 
    files = glob.glob(path+"/*.zip")
    for file in files:
        shutil.unpack_archive(file, re.search(r"\d{4}.*?\.",file).group())
        os.remove(file)
        
def create_list(path): # extract all files into one folder
    allfiles = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            allfiles.append(os.path.join(subdir, file))
    allfiles = [file for file in allfiles if file.endswith("pdf")]
    return allfiles
    
def getword(text):
    pattern = re.compile(r"\b\S+\b")
    return pattern.findall(text)
   
def remove_table(lines):
    """calculate mean length of a line in articles and remove
    all lines that smaller that that and most of the line is digits
    that seem to drop tables"""
    lines = [line.translate(punctuation).strip() for line in lines]# replace line that contains only symbols such as ++ with spaces
    lines = [line for line in lines if len(line)]
    length = []
    for line in lines:
        if len(line):
            length.append(len(line.split()))
    mean_len = np.mean(length)
    std = np.std(length)
    clean = [line for line in lines if len(line.split())>=(mean_len-std) and len(re.findall(r"\d+",line))/len(getword(line))<0.4]
    return clean
    
def extract_txt(file): # conver each pdf to image to capture the whitespaces and extract text from the ocr image.
    try:
        year = int(re.search(r"\d{4}", file).group(0))
        file_name = re.search(r"\d{4}_Q\d{1}", file).group()+"_"+re.search(r"(\d{4}).pdf$",file).group()
        images = convert_from_path(file,poppler_path=poppler_path)
        ocr_text = ''
        for i in range(len(images)):        
            page_content = pytesseract.image_to_string(images[i])
            page_content = '***PDF Page {}***\n'.format(i+1) + page_content
            ocr_text = ocr_text + ' ' + page_content
            lines = ocr_text.splitlines()
            clean = remove_table(lines)
        readability = Readability(" ".join(clean))
        return year, file_name, readability.statistics(),readability.gunning_fog().score
    except: pass
 
if __name__ == '__main__':  
    print(datetime.now().time())
    rootdir = path to your folder with all CCADB files
    #unzip = unzip_file(rootdir)
    pool = mp.Pool(processes=39)
    files = create_list(rootdir)
    files = [file for file in files if "MACOSX" not in file]
    results = [pool.apply_async(extract_txt, [f]) for f in files]
    output = [p.get() for p in results]
    pool.close()
    pool.join()
    print(datetime.now().time())   
    df = pd.DataFrame(output, columns=['year', 'file_name', 'stats',"fog"])
    df.to_csv("CCADB_ALL.csv", index=False)
    print (df.shape)
    

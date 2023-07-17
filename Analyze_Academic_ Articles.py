import glob
import pandas as pd
import numpy as np
from readability import Readability
import re
import os
import time
from datetime import datetime
import multiprocessing as mp
import pytesseract
from pdf2image import convert_from_path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\Program Files\poppler-0.68.0\bin"
#from nltk.corpus import stopwords
#stops = set(stopwords.words('english'))
from nltk.tokenize import sent_tokenize
import string
punctuation = str.maketrans(' ',' ','!\"#$%&()*+/=@[\\\\]^{|}~')

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

def find_end_article(article):
    """stop proccessing with the first occurance from the left of one of the following
    recall that find return -1 in case of failure
    You can also use the None keyword for the end parameter when slicing.
    This would also return the elements till the end of any sequence such as tuple, string, etc.)"""
    stop_at = [article.rfind("Appendix"), article.rfind("References"),article.rfind("Acknowledgements"),\
                article.rfind("NOTES"),article.rfind("Notes")]
    lst = list(filter(lambda x: x!=-1, stop_at))
    if len(lst):
        return np.min(lst) 
    else:
        return None

def filter_sentences(sentences):
    filtered_sentences = []
    for sentence in sentences:
        # Use regular expressions to check if sentence contains any alphanumeric characters
        if re.search(r'[a-zA-Z0-9]+', sentence):
            filtered_sentences.append(sentence)
    return filtered_sentences
    
def remove_table(lines):
    """calculate mean length of a line in articles and remove
    all lines that smaller that that and most of the line is digits
    that seem to drop tables"""
    #lines = [line.translate(punctuation).strip() for line in lines]# replace line that contains only symbols such as ++ with spaces
    #lines = [line for line in lines if len(line)]
    lines = filter_sentences(lines)
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
        year = int(re.search(r"(?<=_)\d{4}", file).group())
        article_name = file.split("\\", 5)[-1]
        article_name = article_name[:re.search("\d{4}",article_name).span()[0]-1].replace("-"," ")
        images = convert_from_path(file,poppler_path=poppler_path, hide_annotations=True, thread_count=5, use_cropbox=True, use_pdftocairo=True)
        ocr_text = ''
        for i in range(len(images)):        
            page_content = pytesseract.image_to_string(images[i])
            page_content = '***PDF Page {}***\n'.format(i+1) + page_content
            ocr_text = ocr_text + ' ' + page_content
        clean = ocr_text[re.search("Introduction",ocr_text, re.I).span()[0]:find_end_article(ocr_text)]
        sents = sent_tokenize(clean)
        clean = remove_table(sents)
        readability = Readability(" ".join(clean))
        return year, article_name, readability.statistics(), readability.gunning_fog().score
    except: print(file)


if __name__ == '__main__':  
    print(datetime.now().time())
    rootdir = Path to your folder containing articles 
    #unzip = unzip_file(rootdir)
    pool = mp.Pool(processes=36)
    files = create_list(rootdir+"\data") # list of pdf files
    files = glob.glob("pathofpdffiles\*")
    # remove none academic articles i.e. call of paper, publisher's note etc.
    files = [file for file in files if "Call-for-" not in file]
    files = [file for file in files if "Editor" not in file]
    files = [file for file in files if not re.search(r"-?Index(_|-)\d{4}", file)]
    files = [file for file in files if "Advertisement" not in file]
    files = [file for file in files if not (re.search(r"Acknowledgement(s)?",file))]
    files = [file for file in files if "Announcement" not in file]
    files = [file for file in files if "Publisher" not in file]
    files = [file for file in files if not re.search(r"Author-index",file, re.I)]
    files = [file for file in files if "Contents" not in file]
    files = [file for file in files if "Corrigendum" not in file]
    files = [file for file in files if not "List-of" in file]
    files = [file for file in files if not "Iddo" in file] # JBF only
    files = [file for file in files if not "Volumes" in file]#only QREF
    files = [file for file in files if not "Book" in file]
    files = [file for file in files if not "Erratum" in file]
    results = [pool.apply_async(extract_txt, args=(f,)) for f in files]
    pool.close()
    pool.join()
    output = [p.get() for p in results]
    print(datetime.now().time())
    df = pd.DataFrame(output, columns=['year', "article_name", 'stats'])
    df.to_csv(DesirePath, index=False)
    print (df.shape)
    

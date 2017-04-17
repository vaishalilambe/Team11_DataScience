# Import the libraries we use.
from bs4 import BeautifulSoup as bsoup
import datetime
import glob
import io
import os
import pandas as pd
import re
import requests
import time
import urllib.request
from urllib.request import urlopen
import zipfile

# Save the initial working directory.
start_directory = os.getcwd()
print(start_directory)

# Create the path to the data directory.
data_directory = os.path.join('../', 'data')
print(data_directory)

# Create logfile.
logfile = open("time_data.txt", "w")
def log_entry(s):
    #print('Date now: %s' % datetime.datetime.now())

    timestamp = '[%s] ' % datetime.datetime.now()
    log_line = timestamp + s + '\n'
    logfile.write(log_line)
    logfile.flush()

    # Also write to standard output as a convenience.
    print(log_line)

site = "https://www.lendingclub.com/info/download-data.action"
#print(site)

response = requests.get(site)
response.raise_for_status()
print(response.status_code)

content = response.content
#print(content[0:200])

try:
    response.raise_for_status()
except Exception as exc:
    print('There was a problem: %s' % (exc))

base_URL = "https://resources.lendingclub.com"
url = urllib.request.urlopen("https://www.lendingclub.com/info/download-data.action")
content = url.read()
#print(content)

soup = bsoup(content, 'html')
#print(soup)

#loanStatsFileNamesJS
fileNameDiv = soup.find('div', {"id":"loanStatsFileNamesJS"})
loanFileList = fileNameDiv.text.rstrip("|")
#print(FileList)

# Set the data directory as the current working directory for the downloads.
os.chdir(data_directory)

# Download and extract all the data files.
for fileName in loanFileList.split("|"):
    #print(fileName)

    csv_filename = fileName
    if csv_filename.endswith('.zip'):
        csv_filename = csv_filename[:-4]

    csv_filepath = os.path.join('.', csv_filename)
    #print(csv_filepath)

    # Download the file if it isn't already in our data directory.
    if os.path.exists(csv_filepath):
        print("Already downloaded %s" % csv_filepath)
    else:
        print("Downloading file %s" % csv_filepath)
        file_URL = base_URL + '/' + fileName
        #print(file_URL)

        zfile = requests.get(file_URL)
        z = zipfile.ZipFile(io.BytesIO(zfile.content))
        z.extractall()

# Restore the working directory
os.chdir(start_directory)

#sample_filepath = os.path.join(data_directory, 'LoanStats3a.csv')
#data = pd.read_csv(sample_filepath, skiprows=1)
#data

def concatenate(indir="./", outfilename="./Accepted_LoanData.csv"):
    initial_working_dir = os.getcwd()
    os.chdir(indir)

    csvFileList = glob.glob("*.csv")
    dfList = []

    # Process the CSV files, without the initial line.
    for csv_filename in csvFileList:
        print(csv_filename)

        # Use the file modification time to track when the data was downloaded.
        timestamp = int(os.path.getmtime(csv_filename))
        #print("last modified: %s" % str(timestamp))

        df = pd.read_csv(csv_filename, low_memory=False, skiprows=1, encoding='latin-1')

        # Add the timestamp into the data.
        df['timestamp'] = timestamp
        print(df.shape)

        dfList.append(df)

    concatDf = pd.concat(dfList, axis=0, copy=False)
    #concatDf.columns = columns
    concatDf.to_csv(outfilename, index=None)
    print(concatDf.shape)

    # Restore the working directory.
    os.chdir(initial_working_dir)

concatenate(indir=data_directory)

import urllib.request
import requests
import zipfile
import io
import os
import glob
import pandas as pd
import re
import requests
import boto
import boto.s3
import sys
import luigi
import datetime, time
import seaborn as sns
import matplotlib as plt
import numpy as np

from boto.s3.key import Key
from urllib.request import urlopen
from bs4 import BeautifulSoup as bsoup

def is_file_present(directory,filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_list = glob.glob(directory+'//*.csv')
    for file_name_in_dir in file_list:
        if (directory+ '\\' + filename) == (file_name_in_dir+".zip"):
            return True
    return False


# In[4]:

def download_data(data_type):
    base_URL = "https://resources.lendingclub.com"
    url = urllib.request.urlopen("https://www.lendingclub.com/info/download-data.action")
    content = url.read()
    soup= bsoup(content,'lxml')
    
    #find div by ID
    fileNameDiv = soup.find('div',{"id":data_type})
    FileList = fileNameDiv.text.rstrip("|")

    for fileName in FileList.split("|"):
        file_URL= base_URL+'/'+fileName
        print(file_URL)
        if not is_file_present(data_type,fileName):    
            zfile = requests.get(file_URL)
            z = zipfile.ZipFile(io.BytesIO(zfile.content))
            z.extractall(data_type)

def read_data(directory):
    fileList = glob.glob(directory+'//*.csv')
    
    dfList=[]
    for filename in fileList:
        print(filename)
        df=pd.read_csv(filename, low_memory=False,skiprows=1,encoding='Latin-1')
        print(df.shape)
        ts = time.time()
        df["download_timestamp"] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        df["recorded_timestamp"] = filename.rstrip('csv').lstrip('rejectedLoanStatsFileNamesJS\\').lstrip('rejectedLoanStatsFileNamesJS\\').lstrip('rejectedLoanStatsFileNamesJS/').lstrip('rejectedLoanStatsFileNamesJS/').lstrip("LoanStats").lstrip("RejectStats").lstrip("_")
        dfList.append(df)
    concatDf=pd.concat(dfList, axis=0)
    #concatDf.columns=columns
    concatDf.to_csv(directory+"_concat_file.csv", index=None)
    print(concatDf.shape)
    return concatDf

def missing_values_table(df):
       mis_val = df.isnull().sum()
       mis_val_percent = 100 * df.isnull().sum()/len(df)
       mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)
       mis_val_table_ren_columns = mis_val_table.rename(
       columns = {0 : 'Missing Values', 1 : '% of Total Values'})
       return mis_val_table_ren_columns


def getAmazonS3keys():
    #Taking data from user
    access_key = input("Please enter your Amazon S3 Access Key ID:")
    secret_key = input("Please enter your Amazon S3 Secret Access Key:")
    return access_key,secret_key


def clean_rejected_data(data):    
	#data = data[pd.notnull(data['loan_amnt'])]    
    
	# ## Handling missing values for categorical variables.


	#cleaning the Emplyment_Length column
	#data['Employment_Length'] = data.Employment_Length.str.replace('+','')
	#data['Employment_Length'] = data.Employment_Length.str.replace('<','')
	#data['Employment_Length'] = data.Employment_Length.str.replace('years','')
	#data['Employment_Length'] = data.Employment_Length.str.replace('year','')
	#data['Employment_Length'] = data.Employment_Length.str.replace('n/a','0')


	#data.Employment_Length.unique()


	#data['Employment_Length'] = data.Employment_Length.map(float)

	strColumns = data.select_dtypes(include=['object']).columns.values
	data[strColumns] = data[strColumns].fillna('Unknown')


	#data.select_dtypes(exclude=[np.number]).isnull().sum()


	#check number of missing values for each numeric column variable
	#data.select_dtypes(include=[np.number]).isnull().sum()


	# ### Handling missing values for numeric variables

	strColumns = data.select_dtypes(include=[np.number]).columns.values
	data[strColumns] = data[strColumns].fillna(data[strColumns].mean())


	data.select_dtypes(include=[np.number]).isnull().sum()
	data.drop(data.columns[0], axis=1) 
	data.head()
	return data


def analysize_approved_data(data):
    data['Amount_Requested'].value_counts() 


    plt.style.use('ggplot')
    get_ipython().magic('matplotlib inline')


    data['Employment_Length'].plot.hist()
    plt.title('Employment Length Distribution')
    plt.ylabel('Frequency')
    plt.xlabel('Employment Length')
    plt.show()


    data['Application_Date'].value_counts().sort_index().plot(kind='line')
    plt.xlabel('Year')
    plt.ylabel('data Volume')
    plt.title('Trends of data Volume')


    data['Risk_Score'].plot.hist()
    plt.title('Employment Length Distribution')
    plt.ylabel('Frequency')
    plt.xlabel('Employment Length')
    plt.show()


    data['Year'] = data['Application_Date'].map(lambda x: 1000*x.year + x.month)


    datas_by_purpose = data.groupby('State')
    print(datas_by_purpose['State'].count())
    datas_by_purpose['State'].count().plot(kind='bar')

    group = data.groupby('data_Title').agg([np.mean])
    data_amt_mean = group['Risk_Score'].reset_index().plot(kind='bar')


    plt.style.use('fivethirtyeight')

    sns.set_style("whitegrid")
    ax = sns.barplot(y = "mean", x = 'grade', data=data_amt_mean)
    ax.set(xlabel = '', ylabel = '', title = 'Average amount dataed, by data grade')
    ax.get_yaxis().set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    _ = ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

class DownloadData(luigi.Task):
 
    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("Rejected_LoanData.csv")
 
    def run(self):
        #loanStatsFileNamesJS
        loan_data = 'rejectedLoanStatsFileNamesJS'

        download_data(loan_data)
        loanData = read_data(loan_data)
        
        loanData.to_csv("Rejected_LoanData.csv", sep=",")

class Cleaning(luigi.Task):
 
    def requires(self):
        return [DownloadData()]
 
    def output(self):
        return luigi.LocalTarget("Cleaned_RejectedLoanData.csv")
 
    def run(self):
        data = pd.read_csv("Rejected_LoanData.csv", low_memory=False,encoding='Latin-1')
        
        #print amount of missing values
        print('Missing values in loan approved data')
        print(missing_values_table(data))
        data = clean_rejected_data(data)
        #Write clean data to new CSV
        data.to_csv("Cleaned_RejectedLoanData.csv", sep=",")

class Exploration(luigi.Task):
    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("Analysis.txt")
 
    def run(self):
        data = pd.read_csv("Cleaned_RejectedLoanData.csv", low_memory=False, encoding='latin-1')

        data = analysize_approved_data(data)


if __name__ == '__main__':
    luigi.run()
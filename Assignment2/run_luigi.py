import luigi
import urllib.request
import requests
import zipfile
import io
import os
import glob
import pandas as pd
import boto
import boto.s3
import sys
import luigi
import datetime, time
import numpy as np
from boto.s3.key import Key
from urllib.request import urlopen
from bs4 import BeautifulSoup as bsoup
import matplotlib.pyplot as plt
import seaborn as sns


def is_file_present(directory,filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_list = glob.glob(directory+'//*.csv')
    for file_name_in_dir in file_list:
        if (directory+ '\\' + filename) == (file_name_in_dir+".zip"):
            return True
    return False

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
        df=pd.read_csv(filename, low_memory=False,skiprows=1,encoding='latin-1')
        print(df.shape)
        ts = time.time()
        df["download_timestamp"] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        df["recorded_timestamp"] = filename.rstrip('csv').lstrip('loanStatsFileNamesJS\\').lstrip('rejectedLoanStatsFileNamesJS\\').lstrip('loanStatsFileNamesJS/').lstrip('rejectedLoanStatsFileNamesJS/').lstrip("LoanStats").lstrip("RejectStats").lstrip("_")
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


def clean_approved_data(data):
    
   # We will fill verification_status_joint using the value in verification_status as these are all individual applications and these values are not filled out.
	data['verification_status_joint'].fillna(data['verification_status'], inplace=True)

	# We will clean the emp_length column to use it in data exploration
	data['emp_length'] = data.emp_length.str.replace('+','')
	data['emp_length'] = data.emp_length.str.replace('<','')
	data['emp_length'] = data.emp_length.str.replace('years','')
	data['emp_length'] = data.emp_length.str.replace('year','')
	data['emp_length'] = data.emp_length.str.replace('n/a','0')

	# We will map it to emp_length to float
	data.emp_length.unique()

	# Convert int_rate datatype to float as we are using it for plotting graphs in data exploration
	data['emp_length'] = data.emp_length.map(float)


	# Only convert int_rate if it isn't already numeric
	if data.int_rate.dtype == 'float64':
		print("int_rate is already numeric, no need to convert it")
    
	elif data.int_rate.dtype == 'object':
		data['int_rate'] = data['int_rate'].map(lambda x: str(x).lstrip(' ').rstrip('% '))
		print(data['int_rate'][0:5])

		data['int_rate'] = data['int_rate'].astype('float64')

	# For the remaining categorical variables we are just going to replace NaN with 'Unknown'.	
	strColumns = data.select_dtypes(include=['object']).columns.values
	data[strColumns] = data[strColumns].fillna('Unknown')

	# see if any null value is present or not for object or not a number data type 
	data.select_dtypes(exclude=[np.number]).isnull().sum()

	#check number of missing values for each numeric column variable
	data.select_dtypes(include=[np.number]).isnull().sum()

	#The first columns that we are going to update are annual_inc_joint, dti_joint. For individual accounts these are blank but we want to use the joint values #so we will populate these with the individual values for individual accounts.
	data[data['application_type'] != 'INDIVIDUAL']['annual_inc_joint'].isnull().sum()
	data['annual_inc_joint'].fillna(data['annual_inc'], inplace=True)
	data['dti_joint'].fillna(data['dti'], inplace=True)

	# For the remaining missing values we are going to fix it by replacing any NaN values with the mean values
	strColumns = data.select_dtypes(include=[np.number]).columns.values
	data[strColumns] = data[strColumns].fillna(data[strColumns].mean())

	data.select_dtypes(include=[np.number]).isnull().sum()

	#features below are being dropped due to their significantly high proportion of missing values or they are date values.

	data = data.drop(['earliest_cr_line', 'last_pymnt_d', 'next_pymnt_d', 'last_credit_pull_d', 'open_acc_6m', 'open_il_6m', 'open_il_12m', 'open_il_24m', 'mths_since_rcnt_il', 'total_bal_il', 'il_util', 'open_rv_24m', 'open_rv_12m', 'max_bal_bc', 'all_util', 'inq_fi', 'total_cu_tl', 'inq_last_12m','mths_since_last_record', 'mths_since_last_major_derog'], axis=1)

	# The URL and description are non-numeric and not useful for predicting interest rates, so drop them.
	data = data.drop(['url', 'desc'], axis=1)

	return data

def analysize_approved_data(data):
    
	# see dictribution of data
	data['int_rate'].hist()

	data.boxplot(column='int_rate')

	data.isnull().sum()

	# see how data amount affects interst rate
	plt.rc("figure", figsize=(6, 4))
	sns.barplot(y='loan_amnt',x="int_rate",data = data[:50])
	plt.title("how 'loan amount' affects 'interest rate' ")
	plt.show()

	# see how annual income affects interst rate
	plt.rc("figure", figsize=(6, 4))
	sns.barplot(y='annual_inc',x="int_rate",data = data[:50])
	plt.title("how 'annual income' affects 'interest rate'")
	plt.show()
	
	# see how term affects interst rate
	plt.rc("figure", figsize=(6, 4))
	sns.barplot(x='term', y="int_rate", data = data)
	plt.title("how 'term' affects 'interest rate'")
	plt.show()

	# see how grade affects interest rate
	data['grade'].unique()
	plt.rc("figure", figsize=(6, 4))
	sns.barplot(x='grade', y="int_rate", data = data, order=["A","B","C","D","E","F","G"])
	plt.title("how 'grade' affects 'interest rate'")
	plt.show()

	data["issue_d"].unique()
	data["issue_d"] = data["issue_d"].str.split("-")
	data["issue_month"] = data["issue_d"].str[0]
	data["issue_year"] = data["issue_d"].str[1]

	# see how issue month affects interest rate
	order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
	sns.barplot(x='issue_month', y="int_rate", data = data, order = order)
	plt.title("how 'issue_month' affects 'interest rate'")
	plt.show()

	# see how issue year affects intrest rate
	sns.barplot(x='issue_year', y="int_rate", data = data)
	plt.title("how 'issue_year' affects 'interest rate'")
	plt.show()

	# see how application type affects interest rate
	plt.rc("figure", figsize=(6, 4))
	sns.boxplot(x='application_type',y="int_rate",data = data)
	plt.title("how 'application type' affects 'interest rate'")
	plt.show()
	data_location = data.zip_code.value_counts()

	data_location.plot(kind = 'bar',figsize=(250,10), title = 'datas per zipcode')

	# distribution of data amount
	plt.rc("figure", figsize=(6, 4))
	data["loan_amnt"].hist()
	plt.title("distribution of data amount")
	plt.show()
	
	# data amount density
	data['loan_amnt'].plot.density()
	plt.xlabel('Amount')
	plt.title('loan Amount Density')
	plt.show()


class DownloadData(luigi.Task):
 
    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("Approved_loans_combinedData.csv")
 
    def run(self):
        #loanStatsFileNamesJS
        loan_data = 'loanStatsFileNamesJS'

        download_data(loan_data)
        loanData = read_data(loan_data)
        
        loanData.to_csv("Approved_loans_combinedData.csv", sep=",")
        

class Cleaning(luigi.Task):
 
    def requires(self):
        return [DownloadData()]
 
    def output(self):
        return luigi.LocalTarget("Cleaned_Approved_loans_combinedData.csv")
 
    def run(self):
        data = pd.read_csv("Approved_loans_combinedData.csv", low_memory=False, encoding='latin-1')
        
        #print amount of missing values
        print('Missing values in loan approved data')
        print(missing_values_table(data))
        data = clean_approved_data(data)
        #Write clean data to new CSV
        data.to_csv("Cleaned_Approved_loans_combinedData.csv", sep=",")

class Exploration(luigi.Task):
    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("Analysis.txt")
 
    def run(self):
        data = pd.read_csv("Cleaned_Approved_loans_combinedData.csv", low_memory=False, encoding='latin-1')

        data = analysize_approved_data(data)

if __name__ == '__main__':
    luigi.run()

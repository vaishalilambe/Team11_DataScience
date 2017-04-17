import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

data_directory = os.path.join('../', 'data')

loan_data_path = os.path.join(data_directory, 'Accepted_LoanData.csv')
loan = pd.read_csv(loan_data_path, low_memory=False, encoding='latin-1')

pd.set_option('display.max_columns', len(loan.columns))
loan.head(3)

pd.reset_option('display.max_columns')
 
# see all loan table column variables datatypes
loan.dtypes

# See shape , all coulmns and statistic values for each columns
print(loan.shape)
print(loan.columns)
print(loan.describe())

# We will fill verification_status_joint using the value in verification_status as these are all individual applications and these values are not filled out.
loan['verification_status_joint'].fillna(loan['verification_status'], inplace=True)

# We will clean the emp_length column to use it in data exploration
loan['emp_length'] = loan.emp_length.str.replace('+','')
loan['emp_length'] = loan.emp_length.str.replace('<','')
loan['emp_length'] = loan.emp_length.str.replace('years','')
loan['emp_length'] = loan.emp_length.str.replace('year','')
loan['emp_length'] = loan.emp_length.str.replace('n/a','0')

# We will map it to emp_length to float
loan.emp_length.unique()

# Convert int_rate datatype to float as we are using it for plotting graphs in data exploration
loan['emp_length'] = loan.emp_length.map(float)


# Only convert int_rate if it isn't already numeric
if loan.int_rate.dtype == 'float64':
    print("int_rate is already numeric, no need to convert it")
    
elif loan.int_rate.dtype == 'object':
    loan['int_rate'] = loan['int_rate'].map(lambda x: str(x).lstrip(' ').rstrip('% '))
    print(loan['int_rate'][0:5])

    loan['int_rate'] = loan['int_rate'].astype('float64')

# For the remaining categorical variables we are just going to replace NaN with 'Unknown'.	
strColumns = loan.select_dtypes(include=['object']).columns.values
loan[strColumns] = loan[strColumns].fillna('Unknown')

# see if any null value is present or not for object or not a number data type 
loan.select_dtypes(exclude=[np.number]).isnull().sum()

#check number of missing values for each numeric column variable
loan.select_dtypes(include=[np.number]).isnull().sum()

#The first columns that we are going to update are annual_inc_joint, dti_joint. For individual accounts these are blank but we want to use the joint values #so we will populate these with the individual values for individual accounts.
loan[loan['application_type'] != 'INDIVIDUAL']['annual_inc_joint'].isnull().sum()
loan['annual_inc_joint'].fillna(loan['annual_inc'], inplace=True)
loan['dti_joint'].fillna(loan['dti'], inplace=True)

# For the remaining missing values we are going to fix it by replacing any NaN values with the mean values
strColumns = loan.select_dtypes(include=[np.number]).columns.values
loan[strColumns] = loan[strColumns].fillna(loan[strColumns].mean())

loan.select_dtypes(include=[np.number]).isnull().sum()

#features below are being dropped due to their significantly high proportion of missing values or they are date values.

loan = loan.drop(['earliest_cr_line', 'last_pymnt_d', 'next_pymnt_d', 'last_credit_pull_d', 'open_acc_6m', 'open_il_6m', 'open_il_12m', 'open_il_24m', 'mths_since_rcnt_il', 'total_bal_il', 'il_util', 'open_rv_24m', 'open_rv_12m', 'max_bal_bc', 'all_util', 'inq_fi', 'total_cu_tl', 'inq_last_12m','mths_since_last_record', 'mths_since_last_major_derog'], axis=1)

# The URL and description are non-numeric and not useful for predicting interest rates, so drop them.
loan = loan.drop(['url', 'desc'], axis=1)

# save cleaned data to .csv
destination_filepath = os.path.join(data_directory, "../Cleaned_AcceptedLoanData.csv")
loan.to_csv(destination_filepath)
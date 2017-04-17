import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data_directory = os.path.join('../', 'data')

#%matplotlib inline
sns.set(style='white', font_scale=0.9)

cleaned_data_path = os.path.join('../', 'Cleaned_AcceptedLoanData.csv')
loan = pd.read_csv(cleaned_data_path, low_memory=False, encoding='latin-1')

loan.head(3)

# see dictribution of loan
loan['int_rate'].hist()

loan.boxplot(column='int_rate')

loan[["loan_amnt","annual_inc"]].dropna().describe()

loan.isnull().sum()

plt.rc("figure", figsize=(6, 4))
sns.barplot(y='loan_amnt',x="int_rate",data = loan[:50])
plt.title("how 'loan amount' affects 'interest rate' ")

plt.rc("figure", figsize=(6, 4))
sns.barplot(y='annual_inc',x="int_rate",data = loan[:50])
plt.title("how 'annual income' affects 'interest rate'")

plt.rc("figure", figsize=(6, 4))
sns.barplot(x='term', y="int_rate", data = loan)
plt.title("how 'term' affects 'interest rate'")

loan['grade'].unique()
plt.rc("figure", figsize=(6, 4))
sns.barplot(x='grade', y="int_rate", data = loan, order=["A","B","C","D","E","F","G"])
plt.title("how 'grade' affects 'interest rate'")

loan["issue_d"].unique()
loan["issue_d"] = loan["issue_d"].str.split("-")
loan["issue_month"] = loan["issue_d"].str[0]
loan["issue_year"] = loan["issue_d"].str[1]

order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
sns.barplot(x='issue_month', y="int_rate", data = loan, order = order)
plt.title("how 'issue_month' affects 'interest rate'")

sns.barplot(x='issue_year', y="int_rate", data = loan)
plt.title("how 'issue_year' affects 'interest rate'")

plt.rc("figure", figsize=(6, 4))
sns.boxplot(x='application_type',y="int_rate",data = loan)
plt.title("how 'application type' affects 'interest rate'")

loan_location = loan.zip_code.value_counts()

loan_location.plot(kind = 'bar',figsize=(250,10), title = 'Loans per zipcode')

plt.rc("figure", figsize=(6, 4))
loan["loan_amnt"].hist()
plt.title("distribution of loan amount")

loan['loan_amnt'].plot.density()
plt.xlabel('Amount')
plt.title('Loan Amount Density')

loan['loan_amnt'].plot.box()
plt.title('Loan Amount Boxplot')
plt.ylabel('Loan Amount')
plt.xlabel('')

loan['loan_status'].value_counts()

loan.groupby('loan_status')['loan_amnt'].sum().sort_values(ascending=0).plot(kind='bar')
plt.xlabel('Loan Status')
plt.ylabel('Loan Amount')
plt.title('What kind of loan status have the largest amount?')

loan['purpose'].value_counts().head(n=10)

loan['title'].value_counts().head(n=10)

loan['grade'].value_counts().sort_index().plot(kind='bar')
plt.title('Loan Grade Volume Distribution')
plt.xlabel('Grade')
plt.ylabel('Volume of Loans')

loan.groupby('grade')['loan_amnt'].sum().sort_index().plot(kind='bar')
plt.title('Loan Grade Amount Distribution')
plt.xlabel('Grade')
plt.ylabel('Amount of Loans')

plt.figure(figsize=(10,5))
plt.scatter(loan['annual_inc'], loan['funded_amnt'])
plt.title("Plotting Annual Income against Funded Amount")
plt.ylabel('Funded Amount')
plt.xlabel('Annual Income')
plt.show()

loan.annual_inc.hist(figsize=(10,5))
plt.ylabel('Number of Loans')
plt.xlabel('Annual Income')

loan = loan[loan['annual_inc']<200000]

loan.annual_inc.hist(figsize=(10,5))
plt.ylabel('Number of Loans')
plt.xlabel('Annual Income')

def CreateDefault(Loan_Status):
    if Loan_Status in ['Current', 'Fully Paid', 'In Grace Period']:
        return 0
    else:
        return 1 
    
loan['Default'] = loan['loan_status'].apply(lambda x: CreateDefault(x))

f, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 3))

sns.distplot(loan[loan['Default'] == 0]['loan_amnt'], bins=40, ax=ax1, kde=False)
sns.distplot(loan[loan['Default'] == 1]['loan_amnt'], bins=40, ax=ax2, kde=False)

ax1.set_title('No Default')
ax2.set_title('Default')

ax1.set_xbound(lower=0)
ax2.set_xbound(lower=0)

plt.tight_layout()
plt.show()

ax1 = sns.violinplot(x='Default', y='loan_amnt', data=loan)
ax1.set_ybound(lower=0)
plt.show()

ax1 = sns.boxplot(x='Default', y='annual_inc', data=loan)
ax1.set_ybound(lower=0)
ax1.set_yscale('log')

plt.show()

ax1 = sns.boxplot(x='Default', y='dti', data=loan)
ax1.set_ybound(lower=0, upper=50)
plt.show()
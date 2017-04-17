
# coding: utf-8

# In[21]:

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

data_directory = os.path.join('.', 'data')

loan_data_path = os.path.join(data_directory, 'Rejected_LoanData.csv')
print(loan_data_path)
loan = pd.read_csv(loan_data_path, low_memory=False, encoding='latin-1') 


# In[22]:

pd.set_option('display.max_columns', len(loan.columns))
loan.head(3) 


# In[23]:

pd.reset_option('display.max_columns')


# In[24]:

loan.dtypes


# In[25]:

print(loan.shape)
print(loan.columns)
print(loan.describe())


# In[26]:

loan.columns = [c.replace(' ', '_') for c in loan.columns]
loan


# ## Handling missing values for categorical variables.

# In[27]:

#cleaning the Emplyment_Length column
loan['Employment_Length'] = loan.Employment_Length.str.replace('+','')
loan['Employment_Length'] = loan.Employment_Length.str.replace('<','')
loan['Employment_Length'] = loan.Employment_Length.str.replace('years','')
loan['Employment_Length'] = loan.Employment_Length.str.replace('year','')
loan['Employment_Length'] = loan.Employment_Length.str.replace('n/a','0')


# In[28]:

loan.Employment_Length.unique()


# In[29]:

loan['Employment_Length'] = loan.Employment_Length.map(float)


# In[30]:

strColumns = loan.select_dtypes(include=['object']).columns.values
loan[strColumns] = loan[strColumns].fillna('Unknown')


# In[31]:

loan.select_dtypes(exclude=[np.number]).isnull().sum()


# In[32]:

#check number of missing values for each numeric column variable
loan.select_dtypes(include=[np.number]).isnull().sum()


# ### Handling missing values for numeric variables

# In[33]:

strColumns = loan.select_dtypes(include=[np.number]).columns.values
loan[strColumns] = loan[strColumns].fillna(loan[strColumns].mean())


# In[34]:

loan.select_dtypes(include=[np.number]).isnull().sum()
#loan.head()
#loan.head()
loan.drop(loan.columns[0], axis=1) 
loan.head()


# In[35]:

loan.to_csv("data/Cleaned_RejectedLoanData.csv")


# ## Exploratory Data Analysis

# In[ ]:

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

data_directory = os.path.join('.', 'data')

loan_data_path = os.path.join(data_directory, 'Cleaned_RejectedLoanData.csv')
loan = pd.read_csv(loan_data_path, low_memory=False, encoding='latin-1')


# In[ ]:

loan['Amount_Requested'].value_counts() 


# In[ ]:

import matplotlib.pyplot as plt
plt.style.use('ggplot')
get_ipython().magic('matplotlib inline')


# In[ ]:

loan['Employment_Length'].plot.hist()
plt.title('Employment Length Distribution')
plt.ylabel('Frequency')
plt.xlabel('Employment Length')
plt.show()


# In[ ]:


loan['Application_Date'].value_counts().sort_index().plot(kind='line')
plt.xlabel('Year')
plt.ylabel('Loan Volume')
plt.title('Trends of Loan Volume')


# In[ ]:

loan['Risk_Score'].plot.hist()
plt.title('Employment Length Distribution')
plt.ylabel('Frequency')
plt.xlabel('Employment Length')
plt.show()


# In[ ]:

loan['Year'] = loan['Application_Date'].map(lambda x: 1000*x.year + x.month)


# In[ ]:

loans_by_purpose = loan.groupby('State')
print(loans_by_purpose['State'].count())
loans_by_purpose['State'].count().plot(kind='bar')


# In[ ]:


group = loan.groupby('Loan_Title').agg([np.mean])
loan_amt_mean = group['Risk_Score'].reset_index().plot(kind='bar')

import seaborn as sns
import matplotlib

plt.style.use('fivethirtyeight')

sns.set_style("whitegrid")
ax = sns.barplot(y = "mean", x = 'grade', data=loan_amt_mean)
ax.set(xlabel = '', ylabel = '', title = 'Average amount loaned, by loan grade')
ax.get_yaxis().set_major_formatter(
matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
_ = ax.set_xticklabels(ax.get_xticklabels(), rotation=0)


# In[ ]:




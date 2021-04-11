#!/usr/bin/env python
# coding: utf-8

# 

# In[1]:


import numpy as np #The Numpy numerical computing library
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
import xlsxwriter #The XlsxWriter libarary for 
import math #The Python math module
from scipy import stats #The SciPy stats module


# 

# In[2]:


stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN


# 

# In[3]:


symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()
data


# 

# In[4]:


pe_ratio = data['peRatio']
pe_ratio


# 

# In[5]:


# Function sourced from 
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]   
        
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

my_columns = ['Ticker', 'Price', 'Price-to-Earnings Ratio', 'Number of Shares to Buy']


# Now we need to create a blank DataFrame and add our data to the data frame one-by-one.

# In[6]:


final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
                                        pd.Series([symbol, 
                                                   data[symbol]['quote']['latestPrice'],
                                                   data[symbol]['quote']['peRatio'],
                                                   'N/A'
                                                   ], 
                                                  index = my_columns), 
                                        ignore_index = True)
        
    
final_dataframe


# 

# In[7]:


final_dataframe.sort_values('Price-to-Earnings Ratio', inplace = True)
final_dataframe = final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace = True)
final_dataframe.drop('index', axis=1, inplace = True)


# 

# In[8]:


def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")


# 

# In[9]:


portfolio_input()


# 

# In[10]:


position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
final_dataframe


# 

# In[11]:


symbol = 'AAPL'
batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=advanced-stats,quote&symbols={symbol}&token={IEX_CLOUD_API_TOKEN}'
data = requests.get(batch_api_call_url).json()

# P/E Ratio
pe_ratio = data[symbol]['quote']['peRatio']

# P/B Ratio
pb_ratio = data[symbol]['advanced-stats']['priceToBook']

#P/S Ratio
ps_ratio = data[symbol]['advanced-stats']['priceToSales']

# EV/EBITDA
enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
ebitda = data[symbol]['advanced-stats']['EBITDA']
ev_to_ebitda = enterprise_value/ebitda

# EV/GP
gross_profit = data[symbol]['advanced-stats']['grossProfit']
ev_to_gross_profit = enterprise_value/gross_profit


# Let's move on to building our DataFrame. You'll notice that I use the abbreviation `rv` often. It stands for `robust value`, which is what we'll call this sophisticated strategy moving forward.

# In[12]:


rv_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy', 
    'Price-to-Earnings Ratio',
    'PE Percentile',
    'Price-to-Book Ratio',
    'PB Percentile',
    'Price-to-Sales Ratio',
    'PS Percentile',
    'EV/EBITDA',
    'EV/EBITDA Percentile',
    'EV/GP',
    'EV/GP Percentile',
    'RV Score'
]

rv_dataframe = pd.DataFrame(columns = rv_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
        ebitda = data[symbol]['advanced-stats']['EBITDA']
        gross_profit = data[symbol]['advanced-stats']['grossProfit']
        
        try:
            ev_to_ebitda = enterprise_value/ebitda
        except TypeError:
            ev_to_ebitda = np.NaN
        
        try:
            ev_to_gross_profit = enterprise_value/gross_profit
        except TypeError:
            ev_to_gross_profit = np.NaN
            
        rv_dataframe = rv_dataframe.append(
            pd.Series([
                symbol,
                data[symbol]['quote']['latestPrice'],
                'N/A',
                data[symbol]['quote']['peRatio'],
                'N/A',
                data[symbol]['advanced-stats']['priceToBook'],
                'N/A',
                data[symbol]['advanced-stats']['priceToSales'],
                'N/A',
                ev_to_ebitda,
                'N/A',
                ev_to_gross_profit,
                'N/A',
                'N/A'
        ],
        index = rv_columns),
            ignore_index = True
        )


# 

# In[13]:


rv_dataframe[rv_dataframe.isnull().any(axis=1)]


# Dealing with missing data is an important topic in data science.
# 
# There are two main approaches:
# 
# * Drop missing data from the data set (pandas' `dropna` method is useful here)
# * Replace missing data with a new value (pandas' `fillna` method is useful here)
# 
# In this tutorial, we will replace missing data with the average non-`NaN` data point from that column. 
# 
# Here is the code to do this:

# In[14]:


for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio','Price-to-Sales Ratio',  'EV/EBITDA','EV/GP']:
    rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace = True)


# Now, if we run the statement from earlier to print rows that contain missing data, nothing should be returned:

# In[15]:


rv_dataframe[rv_dataframe.isnull().any(axis=1)]


# 

# In[16]:


metrics = {
            'Price-to-Earnings Ratio': 'PE Percentile',
            'Price-to-Book Ratio':'PB Percentile',
            'Price-to-Sales Ratio': 'PS Percentile',
            'EV/EBITDA':'EV/EBITDA Percentile',
            'EV/GP':'EV/GP Percentile'
}

for row in rv_dataframe.index:
    for metric in metrics.keys():
        rv_dataframe.loc[row, metrics[metric]] = stats.percentileofscore(rv_dataframe[metric], rv_dataframe.loc[row, metric])/100

# Print each percentile score to make sure it was calculated properly
for metric in metrics.values():
    print(rv_dataframe[metric])

#Print the entire DataFrame    
rv_dataframe


# 

# In[17]:


from statistics import mean

for row in rv_dataframe.index:
    value_percentiles = []
    for metric in metrics.keys():
        value_percentiles.append(rv_dataframe.loc[row, metrics[metric]])
    rv_dataframe.loc[row, 'RV Score'] = mean(value_percentiles)
    
rv_dataframe


# 

# In[18]:


rv_dataframe.sort_values(by = 'RV Score', inplace = True)
rv_dataframe = rv_dataframe[:50]
rv_dataframe.reset_index(drop = True, inplace = True)


# 

# In[19]:


portfolio_input()


# In[20]:


position_size = float(portfolio_size) / len(rv_dataframe.index)
for i in range(0, len(rv_dataframe['Ticker'])-1):
    rv_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / rv_dataframe['Price'][i])
rv_dataframe


# 

# In[21]:


writer = pd.ExcelWriter('value_strategy.xlsx', engine='xlsxwriter')
rv_dataframe.to_excel(writer, sheet_name='Value Strategy', index = False)


# 

# In[22]:


background_color = '#0a0a23'
font_color = '#ffffff'

string_template = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_template = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_template = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

float_template = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

percent_template = writer.book.add_format(
        {
            'num_format':'0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )


# In[23]:


column_formats = {
                    'A': ['Ticker', string_template],
                    'B': ['Price', dollar_template],
                    'C': ['Number of Shares to Buy', integer_template],
                    'D': ['Price-to-Earnings Ratio', float_template],
                    'E': ['PE Percentile', percent_template],
                    'F': ['Price-to-Book Ratio', float_template],
                    'G': ['PB Percentile',percent_template],
                    'H': ['Price-to-Sales Ratio', float_template],
                    'I': ['PS Percentile', percent_template],
                    'J': ['EV/EBITDA', float_template],
                    'K': ['EV/EBITDA Percentile', percent_template],
                    'L': ['EV/GP', float_template],
                    'M': ['EV/GP Percentile', percent_template],
                    'N': ['RV Score', percent_template]
                 }

for column in column_formats.keys():
    writer.sheets['Value Strategy'].set_column(f'{column}:{column}', 25, column_formats[column][1])
    writer.sheets['Value Strategy'].write(f'{column}1', column_formats[column][0], column_formats[column][1])


# 

# In[24]:


import os
if os.path.exists("value_strategy.xlsx"):
    os.remove("value_strategy.xlsx")
writer.save()


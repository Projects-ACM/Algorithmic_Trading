import pandas as pd
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler

apple_stocks = pd.read_csv("/Users/sharonevakharia/PycharmProjects/AlgoTrading/src/resources/s&p_500_historical.csv")

apple_stocks.drop(['Date'], 1)

dim1 = apple_stocks.shape[0]
dim2 = apple_stocks.shape[1]

# numpy array
apple_stocks = apple_stocks.values


# Splitting data into test and train sets
n = apple_stocks.size
train_start = 0
train_end = np.floor(0.60*n)
test_start = train_end
test_end = n

train_data = apple_stocks[np.arrange(train_start, train_end), :]
test_data = apple_stocks[np.arrange[test_start, test_end]]

# Scaling
scaler = MinMaxScaler()

train_data = scaler.fit_transform(train_data)
test_data = scaler.fit_transform(test_data)

x_train = train_data[:, 1]
y_train = train_data[:, 0]

x_test = test_data[:, 1]
y_test = train_data[:, 0]


# Building neural net
n_stocks = 500
x = tf.placeholder(dtype=tf.float32, shape=[None, n_stocks])
y = tf.placeholder(dtype=tf.float32, shape=[None])









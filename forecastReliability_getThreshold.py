import torch
from torch import nn
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import random
import numpy as np
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
from tqdm import tqdm


class TimeSeriesDataset(Dataset):
    def __init__(self, data, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift):
        """
        Args:
            data (torch.Tensor or np.array): time series data, shape (time_steps, features) or (time_steps,)
            input_seq_len (int): number of time steps for input
            output_seq_len (int): number of time steps to predict
        """
        if isinstance(data, np.ndarray):
            data = torch.tensor(data, dtype=torch.float32)

        self.data = data
        self.input_seq_len = input_seq_len
        self.output_seq_len = output_seq_len
        self.input_features_list = input_features_list
        self.input_forecast_features_list = input_forecast_features_list
        self.out_features_list = out_features_list
        self.shift = shift
        self.length = len(data) - input_seq_len - output_seq_len + 1 - self.shift

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        x = self.data[idx : idx + self.input_seq_len, self.input_features_list]
        x_f = self.data[idx + self.input_seq_len + self.shift : idx + self.input_seq_len + self.output_seq_len + self.shift, self.input_forecast_features_list]
        y = self.data[idx + self.input_seq_len + self.shift : idx + self.input_seq_len + self.output_seq_len + self.shift, self.out_features_list]
        
        
        return x, x_f, y

def select_test(train_path='field_f2', test_path='field_f10'):

    df_test = pd.read_csv(test_path)
    df_test.drop('datetime', axis=1, inplace=True)

    return df_test    

def set_data_loader(df_test, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift, batch_size=32):

    # Dummy time series data
    #time_series = np.sin(np.linspace(0, 100, 500))  # shape: (500,)
    time_series_test = df_test.to_numpy()

    scaler = StandardScaler()
    scaler.fit(time_series_test)
    time_series_test = scaler.transform(time_series_test.astype(float))
    #time_series_train = StandardScaler().fit(time_series_train).transform(time_series_train.astype(float))

    dataset_test = TimeSeriesDataset(time_series_test, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift)
    dataloader_test = DataLoader(dataset_test, batch_size=batch_size, shuffle=True)

    return dataloader_test, scaler

def test_model(dataloader_test):

    with torch.inference_mode():
        count = 0
        avg_x_tot = []
        avg_y_tot = []
        var_x_tot = []
        var_y_tot = []
        diff_tot = []


        for x_batch, x_f_batch, y_batch in dataloader_test:
            count += 1
            x_batch = x_batch.type(torch.float32)
            x_f_batch = x_f_batch.type(torch.float32)
            y_batch = y_batch.type(torch.float32)

            avg_x = x_batch.mean(dim=1)[:,0:2]
            avg_y = y_batch.mean(dim=1)
            avg_x_tot.append(avg_x)
            avg_y_tot.append(avg_y)

            diff = abs(avg_x-avg_y)
            diff_tot.append(diff)

            var_x = x_batch.var(dim=1)[:,0:2]
            var_y = y_batch.var(dim=1)
            var_x_tot.append(var_x)
            var_y_tot.append(var_y)


    avg_x_tot = torch.cat(avg_x_tot, dim=0)
    avg_y_tot = torch.cat(avg_y_tot, dim=0)
    var_x_tot = torch.cat(var_x_tot, dim=0)
    var_y_tot = torch.cat(var_y_tot, dim=0)
    diff_tot = torch.cat(diff_tot, dim=0)

    print(f"Done!!  -  {count}")

    return avg_x_tot, avg_y_tot, var_x_tot, var_y_tot, diff_tot


input_seq_len = 24 # dataset
output_seq_len = 24 # dataset
input_features_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14] # dataset
input_forecast_features_list = [24,25,26,27,28,29,30] # dataset
out_features_list = [0,1] # dataset
shift = 24 #dataset

#model
input_size = len(input_features_list)
forecast_size = len(input_forecast_features_list)
output_size = len(out_features_list)
hidden_size = 20
model_path = 'weights/model_weights_24_output_seq_len_24_shift_0.pth'

df_test = select_test(test_path='code/fields/field_f10')
dataloader_test, scaler = set_data_loader(df_test, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift, 1)

avg_x_tot, avg_y_tot, var_x_tot, var_y_tot, diff_tot = test_model(dataloader_test)

avg_x_tot = avg_x_tot[:,0]
avg_y_tot = avg_y_tot[:,0]
var_x_tot = var_x_tot[:,0]
var_y_tot = var_y_tot[:,0]


fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# Flatten the axes array for easy iteration
axes = axes.flatten()

# Plot histograms
datasets = [avg_x_tot, avg_y_tot, var_x_tot, var_y_tot]
titles = ['avg x', 'avg y', 'var x', 'var y']

for ax, data, title in zip(axes, datasets, titles):
    ax.hist(data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.6)

# Adjust layout for better spacing
plt.tight_layout()
plt.show()


# Plot histogram
x_np = diff_tot.numpy()
plt.hist(x_np[:,1], bins=30, color='skyblue', edgecolor='black')
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.title("Histogram of Tensor Values")
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()



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

def load_pytorch_model(model_path, input_size, hidden_size, output_size, forecast_size, output_seq_len):
    

    class Encoder(nn.Module):
        def __init__(self, input_size, hidden_size):
            super(Encoder, self).__init__()
            self.rnn = nn.RNN(input_size=input_size, hidden_size=hidden_size, batch_first=True)

        def forward(self, x):
            # x: (batch_size, input_seq_len, input_size)
            outputs, hidden = self.rnn(x)  # hidden: (1, batch, hidden_size)
            return hidden


    class Decoder(nn.Module):
        def __init__(self, output_size, hidden_size, forecast_size):
            super(Decoder, self).__init__()
            self.rnn = nn.RNN(input_size=output_size+forecast_size, hidden_size=hidden_size, batch_first=True)
            self.fc = nn.Linear(hidden_size, output_size)

        def forward(self, decoder_input, hidden):
            # decoder_input: (batch_size, 1, output_size) ← one timestep
            output, hidden = self.rnn(decoder_input, hidden)
            output = self.fc(output)  # (batch_size, 1, output_size)
            return output, hidden


    class Seq2Seq(nn.Module):
        def __init__(self, encoder, decoder, output_seq_len):
            super(Seq2Seq, self).__init__()
            self.encoder = encoder
            self.decoder = decoder
            self.output_seq_len = output_seq_len

        def forward(self, x, x_f):
            batch_size = x.size(0)
            output_size = self.decoder.fc.out_features
            
            hidden = self.encoder(x)

            # Start with zeros or a special <START> token
            decoder_input = torch.zeros(batch_size, 1, output_size, device=x.device)

            outputs = []

            for i in range(self.output_seq_len):
                current_x_f = x_f[:,i,:].unsqueeze(dim=1)
                decoder_input = torch.cat((decoder_input, current_x_f), dim=2)
                output, hidden = self.decoder(decoder_input, hidden)
                outputs.append(output)
                decoder_input = output  # Teacher forcing could go here

            return torch.cat(outputs, dim=1)


    encoder = Encoder(input_size, hidden_size)
    decoder = Decoder(output_size, hidden_size, forecast_size)
    model = Seq2Seq(encoder, decoder, output_seq_len)
    model.load_state_dict(torch.load(model_path))
    model.eval() 

    print(f"Model loaded successfully from {model_path}")
    return model

def test_model(model, dataloader_test, scaler):

    th=0.3

    criterion = nn.MSELoss()

    with torch.inference_mode():
        # 1. Forward pass
        count = 0
        avg_x_tot = []
        avg_y_tot = []
        diff_tot = []

        high_diff_y = []
        high_diff_out = []
        low_diff_y = []
        low_diff_out = []


        for x_batch, x_f_batch, y_batch in dataloader_test:
            count += 1
            x_batch = x_batch.type(torch.float32)
            x_f_batch = x_f_batch.type(torch.float32)
            y_batch = y_batch.type(torch.float32)
            
            # Forward pass
            outputs = model(x_batch, x_f_batch)

            avg_x = x_batch.mean(dim=1)[:,0:2]
            avg_y = y_batch.mean(dim=1)
            avg_x_tot.append(avg_x)
            avg_y_tot.append(avg_y)

            diff = abs(avg_x-avg_y)
            diff_tot.append(diff)

            if diff[0][0] > th:
                high_diff_y.append(y_batch)
                high_diff_out.append(outputs)
            else:
                low_diff_y.append(y_batch)
                low_diff_out.append(outputs)

    high_diff_y = torch.cat(high_diff_y, dim=0)
    high_diff_out = torch.cat(high_diff_out, dim=0)
    low_diff_y = torch.cat(low_diff_y, dim=0)
    low_diff_out = torch.cat(low_diff_out, dim=0)

    print(f"Done!!  -  {count}")

    return high_diff_y, high_diff_out, low_diff_y, low_diff_out




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

model = load_pytorch_model(model_path, input_size, hidden_size, output_size, forecast_size, output_seq_len)
df_test = select_test(test_path='code/fields/field_f10')
dataloader_test, scaler = set_data_loader(df_test, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift, 1)

high_diff_y, high_diff_out, low_diff_y, low_diff_out = test_model(model, dataloader_test, scaler)

high_diff = abs(high_diff_y - high_diff_out)
low_diff = abs(low_diff_y - low_diff_out)
high_diff = high_diff.mean(dim=1)[:,0]
low_diff = low_diff.mean(dim=1)[:,0]


fig, axes = plt.subplots(1, 2, figsize=(10, 8))
axes = axes.flatten()
datasets = [high_diff, low_diff]
titles = ['high_diff', 'low_diff']

for ax, data, title in zip(axes, datasets, titles):
    ax.hist(data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.6)

# Adjust layout for better spacing
plt.tight_layout()
plt.show()


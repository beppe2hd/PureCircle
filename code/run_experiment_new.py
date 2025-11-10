import torch
from torch import nn
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import random
import numpy as np
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
from tqdm import tqdm




def select_train_test(train_path='field_f2', test_path='field_f10'):
    df_train = pd.read_csv(train_path)
    df_train.drop('datetime', axis=1, inplace=True)
    #print(df_train.shape)
    #print(df_train.columns)

    df_test = pd.read_csv(test_path)
    df_test.drop('datetime', axis=1, inplace=True)
    #print(df_test.shape)
    #print(df_test.columns)

    return df_train, df_test


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
    

def set_data_loader(df_train, df_test, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift):

    # Dummy time series data
    #time_series = np.sin(np.linspace(0, 100, 500))  # shape: (500,)
    time_series_train = df_train.to_numpy()
    time_series_test = df_test.to_numpy()

    scaler = StandardScaler()
    scaler.fit(time_series_train)
    time_series_train = scaler.transform(time_series_train.astype(float))
    time_series_test = scaler.transform(time_series_test.astype(float))
    #time_series_train = StandardScaler().fit(time_series_train).transform(time_series_train.astype(float))


    dataset_train = TimeSeriesDataset(time_series_train, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift)
    dataloader_train = DataLoader(dataset_train, batch_size=32, shuffle=True)

    dataset_test = TimeSeriesDataset(time_series_test, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift)
    dataloader_test = DataLoader(dataset_test, batch_size=32, shuffle=True)

    return dataloader_train, dataloader_test
    

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



def train(dataloader_train, dataloader_test, input_size, output_size, forecast_size, hidden_size, output_seq_len, epochs):
    encoder = Encoder(input_size, hidden_size)
    decoder = Decoder(output_size, hidden_size, forecast_size)
    model = Seq2Seq(encoder, decoder, output_seq_len)

    #x = torch.randn(32, input_seq_len, input_size)
    #y = model(x)
    #print(y.shape)  

    optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9, weight_decay=1e-4)
    criterion = nn.MSELoss()
    train_losses = np.zeros(epochs)
    test_losses = np.zeros(epochs)
    mse_overEpoches = np.zeros(epochs)

    for epoch in tqdm(range(epochs)):
        model.train()
        train_loss = 0.
        count = 0
        for x_batch, x_f_batch, y_batch in dataloader_train:
            count += 1
            x_batch = x_batch.type(torch.float32)
            x_f_batch = x_f_batch.type(torch.float32)
            y_batch = y_batch.type(torch.float32)
            # Forward pass
            outputs = model(x_batch, x_f_batch)

            loss = criterion(outputs, y_batch)
            train_loss += loss.item()

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        train_losses[epoch] = train_loss / count

        model.eval()
        with torch.inference_mode():
            # 1. Forward pass
            test_loss = 0.
            mse_s = 0.
            count = 0
            for x_batch, x_f_batch, y_batch in dataloader_test:
                count += 1
                x_batch = x_batch.type(torch.float32)
                x_f_batch = x_f_batch.type(torch.float32)
                y_batch = y_batch.type(torch.float32)
                # Forward pass
                outputs = model(x_batch, x_f_batch)

                loss = criterion(outputs, y_batch)
                test_loss += loss.item()
                mse = torch.mean((y_batch - outputs) ** 2)
                mse_s += mse

            mse_overEpoches[epoch] = mse_s / count
            test_losses[epoch] = test_loss / count


    return test_losses[-1], model



#######################
##
##   Run Experiment
##
#######################


# Define the seed value
seed = 42

# Set seed for PyTorch
torch.manual_seed(seed)

# Set seed for CUDA (if using GPUs)
torch.cuda.manual_seed(seed)
torch.cuda.manual_seed_all(seed)  # For multi-GPU setups

# Set seed for Python's random module
random.seed(seed)

# Set seed for NumPy
np.random.seed(seed)

# Ensure deterministic behavior for PyTorch operations
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False




input_seq_len = 30 # dataset
output_seq_len = 12 # dataset
input_features_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14] # dataset
input_forecast_features_list = [24,25,26,27,28,29,30] # dataset
out_features_list = [0,1] # dataset
shift = 24 #dataset

#model
input_size = len(input_features_list)
forecast_size = len(input_forecast_features_list)
output_size = len(out_features_list)
hidden_size = 20

epochs = 30

collection = []

for input_seq_len in [24]:
    for output_seq_len in [24]:
        for shift in [24]:

            df_train, df_test = select_train_test(train_path='code/fieldsComplete/field_f2', test_path='code/fieldsComplete/field_f10')
            dataloader_train, dataloader_test = set_data_loader(df_train, df_test, input_seq_len, output_seq_len, input_features_list, input_forecast_features_list, out_features_list, shift)
            loss_mse, model = train(dataloader_train, dataloader_test, input_size, output_size, forecast_size, hidden_size, output_seq_len, epochs)

            out = {'input_seq_len': input_seq_len, 'output_seq_len': output_seq_len, 'shift': shift, 'MSE': loss_mse}
            torch.save(model.state_dict(), f"models/model_weights_{input_seq_len}_output_seq_len_{shift}.pth")

            collection.append(out)

print(collection)  

import json
# Save dictionary as JSON
with open("out.json", "w") as f:
    json.dump(collection, f, indent=4)
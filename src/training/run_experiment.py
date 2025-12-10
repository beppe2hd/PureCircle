import torch
from torch import nn
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import random
import numpy as np
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
from tqdm import tqdm
import joblib
import yaml
import argparse
import os
from commons.trainingObjects.loadObj import load_Optimizer, load_Loss

from commons.architectures.create_model import create_model


def get_config_file():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configFile", type=str, required=True)
    args = parser.parse_args()
    with open(args.name, "r") as f:
        config = yaml.safe_load(f)
    return config


#######################
##
##   Run Experiment
##
#######################
def set_randomness():
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


def load_train_test(train_path, test_path):
    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)
    return df_train, df_test


class TimeSeriesDataset(Dataset):
    def __init__(self, data, config):
        """
        Args:
            data (pandas.Dataframe)
        """
        # if isinstance(data, np.ndarray):
        #    data = torch.tensor(data, dtype=torch.float32)

        self.data = data
        self.input_seq_len = config["features"]["input_seq_len"]
        self.output_seq_len = config["features"]["output_seq_len"]
        self.input_features_list = (
            config["features"]["input"]["fiedls"]
            + config["features"]["input"]["meteo_historical"]
        )
        self.input_forecast_features_list = config["features"]["input"][
            "meteo_forecast"
        ]
        self.out_features_list = config["features"]["output"]
        self.shift = config["features"]["shift"]
        self.length = len(data) - input_seq_len - output_seq_len + 1 - self.shift

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        x = self.data[self.input_features_list]
        x = torch.tensor(x, dtype=torch.float32)
        x = x[idx : idx + self.input_seq_len, :]

        x_f = self.data[self.input_forecast_features_list]
        x_f = torch.tensor(x_f, dtype=torch.float32)
        x_f = x_f[
            idx
            + self.input_seq_len
            + self.shift : idx
            + self.input_seq_len
            + self.output_seq_len
            + self.shift,
            :,
        ]

        y = self.data[self.out_features_list]
        y = torch.tensor(y, dtype=torch.float32)
        y = self.data[
            idx
            + self.input_seq_len
            + self.shift : idx
            + self.input_seq_len
            + self.output_seq_len
            + self.shift,
            :,
        ]

        return x, x_f, y


def inverse_scale_data(output, cols):

    mean = scaler.mean_[cols]
    std = scaler.scale_[cols]

    std = std.view(1, len(cols), 1)  # → shape [1, 2, 1]
    mean = mean.view(1, len(cols), 1)

    output = output * std + mean

    return output


def scale_data(df_train, df_test):

    scaler = StandardScaler()
    scaler.fit(df_train)

    df_train = scaler.transform(df_train)
    df_test = scaler.transform(df_test)

    df_train = pd.DataFrame(df_train, columns=df_train.columns, index=df_train.index)
    df_test = pd.DataFrame(df_test, columns=df_test.columns, index=df_test.index)

    return df_train, df_test, scaler


def set_data_loaders(config, df_train, df_test):

    dataset_train = TimeSeriesDataset(config, df_train)
    dataloader_train = DataLoader(dataset_train, batch_size=32, shuffle=True)

    dataset_test = TimeSeriesDataset(config, df_test)
    dataloader_test = DataLoader(dataset_test, batch_size=32, shuffle=True)

    return dataloader_train, dataloader_test


def data_preparation(config):

    path_train = config["files"]["training"]
    path_test = config["files"]["test"]

    df_train, df_test = load_train_test(path_train, path_test)

    selected_columns = list(
        set(
            config["features"]["input"]["fiedls"]
            + config["features"]["input"]["meteo_historical"]
            + config["features"]["input"]["meteo_forecast"]
            + config["features"]["output"]
        )
    )
    targets = config["features"]["output"]
    output_scale_index = [selected_columns.index(t) for t in targets]

    if all(item in df_train.columns for item in selected_columns):
        df_train = df_train[selected_columns]
    else:
        print("Not all items are contained in train columns")
        print(f"Train Columns: {df_train.columns}")
        print(f"Selected_columns: {selected_columns}")

    if all(item in df_test.columns for item in selected_columns):
        df_test = df_test[selected_columns]
    else:
        print("Not all items are contained in train columns")
        print(f"Train Columns: {df_test.columns}")
        print(f"Selected_columns: {selected_columns}")

    df_train, df_test, scaler = scale_data(df_train, df_test)
    dataloader_train, dataloader_test = set_data_loaders(config, df_train, df_test)

    return dataloader_train, dataloader_test, scaler, output_scale_index


def train(config, dataloader_train, dataloader_test, output_scale_index, scaler):

    model = create_model(config)

    optimizer = load_Optimizer(model, config)
    criterion = load_Loss(config)
    epochs = config["hyperparameters"]["epoches"]

    train_losses = np.zeros(epochs)
    test_losses = np.zeros(epochs)
    mse_overEpoches = np.zeros(epochs)

    for epoch in tqdm(range(epochs)):
        model.train()
        train_loss = 0.0
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
            test_loss = 0.0
            mse_s = 0.0
            count = 0
            for x_batch, x_f_batch, y_batch in dataloader_test:
                count += 1
                x_batch = x_batch.type(torch.float32)
                x_f_batch = x_f_batch.type(torch.float32)
                y_batch = y_batch.type(torch.float32)
                # Forward pass
                outputs = model(x_batch, x_f_batch)

                ## apply inverse_scale_data(output, col)
                outputs = inverse_scale_data(outputs, output_scale_index, scaler)
                y_batch = inverse_scale_data(y_batch, output_scale_index, scaler)

                loss = criterion(outputs, y_batch)
                test_loss += loss.item()
                mse = torch.mean((y_batch - outputs) ** 2)
                mse_s += mse

            mse_overEpoches[epoch] = mse_s / count
            test_losses[epoch] = test_loss / count

    return model, loss_mse


def save(config, model, scaler, loss_mse):

    folder_path = "./weights/" + config["name"] + config["version"].replace(".", "_")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Folder created:", folder_path)
    else:
        print("Folder already exists.")

    path_model = folder_path + "/weights.pth"
    path_scaler = folder_path + "/scaler.pkl"
    torch.save(model.state_dict(), path_model)
    joblib.dump(scaler, path_scaler)

    ## complete with a text file reporting information on loss


if __name__ == "__main__":
    set_randomness()
    config = get_config_file()
    dataloader_train, dataloader_test, scaler = data_preparation(config)
    model, scaler, loss_mse = train(config, dataloader_train, dataloader_test)
    save(config, model, scaler, loss_mse)

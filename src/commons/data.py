import torch

def inverse_scale_data(output, cols, scaler):

    mean = torch.tensor(scaler.mean_[cols])
    std = torch.tensor(scaler.scale_[cols])

    std = std.view(1, 1, len(cols))  # → shape [1, 2, 1]
    mean = mean.view(1, 1, len(cols))

    output = output * std + mean

    return output


def specific_scale_data(input, cols, scaler):

    mean = torch.tensor(scaler.mean_[cols])
    std = torch.tensor(scaler.scale_[cols])

    std = std.view(1, 1, len(cols))  # → shape [1, 2, 1]
    mean = mean.view(1, 1, len(cols))

    input = (input - mean) / std

    return input
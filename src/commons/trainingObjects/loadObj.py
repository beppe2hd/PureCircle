import torch
from torch import nn

available_optimizers = ["SGD", "Adam"]
available_losses = ["MSELoss", "Huber"]


def load_Optimizer(model, config):

    oprimizer_type = config["hyperparameters"]["optimizer"]
    lr = config["hyperparameters"]["learning_rate"]
    momentum = config["hyperparameters"]["momentum"]
    weight_decay = config["hyperparameters"]["weight_decay"]

    if oprimizer_type in available_optimizers:

        if oprimizer_type == "SGD":

            optimizer = torch.optim.SGD(
                model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay
            )
    
        if oprimizer_type == "Adam":

            optimizer = torch.optim.Adam(
                model.parameters(), lr=lr, weight_decay=weight_decay
            )

        return optimizer

    else:
        print(
            f"Optimizer {oprimizer_type}, not available, chose one in {available_optimizers}"
        )


def load_Loss(config):

    loss_type = config["hyperparameters"]["loss"]

    if loss_type in available_losses:

        if loss_type == "MSELoss":
            criterion = nn.MSELoss()

        if loss_type == "MAPE":
            def mape(y_pred, y_true, epsilon=1e-8):
                return torch.mean(torch.abs((y_true - y_pred) / (y_true + epsilon))) * 100
            criterion = mape

        if loss_type == "Huber":
            criterion = nn.HuberLoss(delta=1.0)

    return criterion

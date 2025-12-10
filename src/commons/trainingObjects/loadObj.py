import torch
from torch import nn

available_optimizers = ['SGD']
available_losses = ['MSELoss']

def load_Optimizer(model, config):

    oprimizer_type = config["hyperparameters"]["oprimizer"]
    lr = config["hyperparameters"]["learning_rate"]
    momentum = config["hyperparameters"]["momentum"]
    weight_decay = config["hyperparameters"]["weight_decay"]

    if oprimizer_type in available_optimizers:

        if oprimizer_type == 'SGD':


            optimizer = torch.optim.SGD(
                    model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay
                )
            
        return optimizer
    
    else: print(f"Optimizer {oprimizer_type}, not available, chose one in {available_optimizers}")


def load_Loss(config)
    

    loss_type = config["hyperparameters"]["loss"]
    
    if loss_type in available_losses:
        
        if loss_type == "MSELoss":
            criterion = nn.MSELoss()

    return criterion
[Back to home](../README.md)

# AI Model

The AI model is a time-series forecasting network designed to ingest historical observations from in-field sensors, together with current and forecasted weather conditions, in order to predict future soil moisture levels. These predictions provide a quantitative basis for the Decision Support System (DSS), enabling the generation of actionable irrigation recommendations.

## Input/Output data structure:
The input and output data structures depend on the specific set of selected input features, the desired output variables, and the sizes of the input observation window and the output forecast window, allowing the model configuration to be adapted to different forecasting needs.

<img src="../images/data.png" width="600">

| Parameter | Description |
|------------|-------------|
| **input len** | Number of past time steps used as input (length of observation window). |
| **input size** | Number of input features (e.g., soil moisture, irrigation events, solar radiation, temperature…). |
| **output len** | Number of future time steps to predict (forecast horizon). |
| **output size** | Number of target features to predict (e.g., soil moisture in and between crop rows). |
| **shift** | Temporal gap (in time steps) between the end of the input window and the start of the prediction window. A positive shift introduces a delay between observation and prediction. |

## Network Architecture
The adopted neural network is based on an Encoder–Decoder architecture, which enables flexible and task-specific forecasting. This design allows the model to adapt dynamically to variations in:
- Input and output sequence lengths
- Number of input and output features

<img src="../images/net.png" width="600">

Such flexibility supports customized, ad hoc forecasting of environmental and crop-related variables under heterogeneous irrigation regimes.
At the core of the architecture, Long Short-Term Memory (LSTM) cells are employed. LSTMs provide an effective trade-off between model expressiveness and robustness, particularly in scenarios characterized by limited data availability and long-term temporal dependencies. Their gated structure enables the model to retain relevant historical information while mitigating vanishing gradient issues commonly encountered in standard recurrent networks.
Preliminary experiments with more complex architectures (e.g., deeper or higher-capacity models) resulted in overfitting, primarily due to the constrained size and variability of the available datasets. Consequently, the LSTM-based Encoder–Decoder configuration was selected as the most reliable and generalizable solution for the considered forecasting tasks.

## Files

This repository contains the main scripts and notebooks used for **data preparation**, **model training**, and **result visualization**.  
Each component plays a specific role in the experimental workflow — from transforming raw field and meteorological data into structured datasets, to training predictive models and analyzing their performance.

| File | Description |
|------|--------------|
| **`createDataset.ipynb`** | Jupyter notebook that generates a **complete and clean dataset** (CSV format) for each experimental field. It reads and merges data from the provided `.xlsx` source files (soil moisture, irrigation events, meteorological data, and LAI) into unified time-series datasets ready for modeling. |
| **`run_experiments.py`** | Main Python script to **train forecasting models** using the prepared datasets. It handles data loading, model configuration, and training routines, and automatically saves the trained model weights into the `weights/` directory. |
| **`plotResults.py`** | Script for **visualizing and analyzing model outputs**. It loads predictions and observed data to produce performance plots (e.g., time series comparisons, error metrics, or evaluation summaries). Useful for assessing and comparing model performance across irrigation strategies and quinoa varieties. |
| **`forecastReliability_getThreshold.py`** | This file load a specific model with its specific configuration and plot the distribution: 1) the mean of the differenc between the soil moisture in observation windows and in GT forecast, 2) the mean and variance of soil moisture in observation windows and in GT forecast. |
| **`forecastReliability_testThreshold.py`** | Given a threshold discriminating sudden changes between the sm in the observation windows and the forecast GT this script show the distribution of the error for bot cases. In other tarns this shows the error magnitude in case of small changes between the observation windows and the forecast GT and the magnitude of the error when this change in more evident. |
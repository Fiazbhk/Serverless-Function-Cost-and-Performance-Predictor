# Serverless Function Cost and Performance Predictor

A data analysis and machine learning project that examines real-world Azure Functions invocation data to understand serverless workload patterns and predict function-level cost using invocation behavior.

## Overview

Serverless computing platforms charge based on how frequently a function is invoked, how long it executes, and how much memory it consumes. This project investigates whether function cost can be estimated from invocation patterns alone, using the publicly released Azure Functions 2019 trace dataset.

The analysis covers data loading and cleaning at scale, exploratory analysis of invocation and application-level patterns, engineering of a cost proxy metric based on serverless billing principles, and development of a Random Forest regression model to predict cost from invocation frequency and trigger type.

## Dataset

This project uses the Azure Functions Dataset 2019, released publicly by Microsoft as part of the Azure Public Dataset repository.

- Source repository: https://github.com/Azure/AzurePublicDataset
- Dataset documentation: https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsDataset2019.md
- Kaggle mirror used in this project: https://www.kaggle.com/datasets/theodoram/azure-2019-public-dataset

Reference paper:
Shahrad, M., Fonseca, R., Goiri, I., Chaudhry, G., Batum, P., Cooke, J., Laureano, E., Tresness, C., Russinovich, M., and Bianchini, R. Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider. Proceedings of the 2020 USENIX Annual Technical Conference (USENIX ATC 20), USENIX Association, Boston, MA, July 2020.

The dataset consists of three files:

| File | Description |
|---|---|
| invocations_per_function_md.feather | Minute-level invocation counts per function over 14 days |
| function_durations_percentiles.feather | Daily execution duration statistics per function |
| app_memory_percentiles.feather | Daily memory allocation statistics per application |

## Project Objectives

1. Load and explore Azure Functions invocation data
2. Analyze invocation frequency patterns across functions and applications
3. Engineer features that relate to cost and performance
4. Build a predictive model for function invocation load
5. Summarize findings and business relevance

## Methodology

### Data Loading
The raw invocation file contains 1,440 minute-level columns per function, which exceeded the memory limits of a standard pandas workflow. This was resolved using PyArrow for memory-mapped file access and DuckDB for in-process aggregation, allowing the dataset to be summarized without loading the full raw file into memory.

### Feature Engineering
The invocation, duration, and memory datasets were merged at the function and application level. A cost proxy metric was engineered by combining average memory allocation, average execution duration, and total invocations, following the general structure of serverless billing models. Additional performance features, including duration variability, were also derived.

### Data Leakage Correction
An initial model trained using duration and memory features alongside invocation data achieved an unrealistically high R-squared of 0.9993. This was identified as data leakage, since the target variable was directly derived from those same features. The model was rebuilt using only invocation frequency and trigger type, features that would realistically be available before detailed execution data exists for a function.

### Modeling
A Random Forest regression model was trained on the corrected feature set to predict a log-transformed cost proxy. The model was evaluated using R-squared, mean absolute error, and root mean squared error on a held-out test set.

## Results

| Metric | Value |
|---|---|
| R-squared | 0.4785 |
| Mean Absolute Error | 1.3125 |
| Root Mean Squared Error | 1.6981 |

Total invocations and average invocations per minute together account for approximately 79 percent of the model's predictive weight, confirming invocation volume as the dominant signal for cost estimation. Trigger type contributes secondary predictive value, with queue and timer-based functions showing slightly higher influence than other categories.

## Key Findings

- Serverless workloads are highly skewed, with a small number of functions and applications responsible for the majority of invocation volume and cost
- Invocation frequency alone explains close to half of the variance in function cost, even without duration or memory information
- Trigger type provides secondary predictive value beyond invocation frequency
- The model systematically underpredicts extremely high-cost functions, indicating that factors beyond invocation frequency influence cost at the upper end of the distribution

## Repository Structure

```
.
├── Serverless_Function_Cost_and_Performance_Predictor.ipynb   Main analysis notebook
├── Serverless_Cost_Predictor_Report.docx                      Full project report
└── README.md
```

## Tools and Libraries

- Python
- Pandas
- PyArrow
- DuckDB
- NumPy
- Matplotlib
- Scikit-learn

## How to Run

1. Clone this repository
2. Open the notebook in Google Colab or a local Jupyter environment
3. Download the dataset from the Kaggle link above and place it in the expected directory, or use the Kaggle API as demonstrated in the notebook
4. Run the notebook cells sequentially

## Author

Muhammad Fiaz

import pandas as pd
import numpy as np
from scipy import stats


def validate_data(df):
    ":param df: DataFrame containing the experiment data"
    if df.isnull().values.any():
        raise ValueError("Data contains NaN values. Please clean the data.")
    if 'group' not in df.columns or 'result' not in df.columns:
        raise ValueError("DataFrame missing required columns: 'group' and 'result'.")


def calculate_confidence_interval(data, confidence=0.95):
    """
    Calculate the confidence interval for the given data.
    :param data: Sample data
    :param confidence: Confidence level (default is 0.95)
    :return: Tuple containing the lower and upper bounds of the confidence interval
    """
    mean = np.mean(data)
    sem = stats.sem(data)
    h = sem * stats.t.ppf((1 + confidence) / 2., len(data) - 1)
    return mean - h, mean + h


def perform_t_test(group1, group2):
    """
    Perform a t-test between two groups.
    :param group1: Results of the first group
    :param group2: Results of the second group
    :return: t-statistic and p-value
    """
    t_stat, p_value = stats.ttest_ind(group1, group2)
    return t_stat, p_value


def main_experiment_analysis(df):
    validate_data(df)
    
    # Split the data into two groups
    group1 = df[df['group'] == 'A']['result']
    group2 = df[df['group'] == 'B']['result']
    
    # Perform t-test
    t_stat, p_value = perform_t_test(group1, group2)
    
    # Calculate confidence intervals
    ci_group1 = calculate_confidence_interval(group1)
    ci_group2 = calculate_confidence_interval(group2)
    
    # Print results
    print(f"T-statistic: {t_stat}, P-value: {p_value}")
    print(f"Group A CI: {ci_group1}, Group B CI: {ci_group2}")
    
    # Check significance
    if p_value < 0.05:
        print("Statistically significant difference between groups.")
    else:
        print("No statistically significant difference.")


if __name__ == "__main__":
    # Example usage of main_experiment_analysis
    # df = pd.read_csv('path/to/your/data.csv')
    # main_experiment_analysis(df)

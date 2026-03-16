import pandas as pd
import numpy as np
import argparse
import json
import os
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def load_config(config_path='config.json'):
    """
    Load configuration parameters from a JSON file.
    :param config_path: Path to the configuration file
    :return: Dictionary containing configuration parameters
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Warning: Configuration file '{config_path}' not found. Using defaults.")
        return {
            'confidence_level': 0.95,
            'significance_threshold': 0.05,
            'test_type': 'auto',
            'output_dir': 'results'
        }
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in configuration file '{config_path}'.")
        return None

def validate_data(df, group_col='group', result_col='result'):
    """
    Validate the input dataframe for required columns and data quality.
    :param df: DataFrame containing the experiment data
    :param group_col: Name of the group column
    :param result_col: Name of the result column
    """
    if df.empty:
        raise ValueError("DataFrame is empty.")
    if df.isnull().values.any():
        raise ValueError("Data contains NaN values. Please clean the data.")
    if group_col not in df.columns or result_col not in df.columns:
        raise ValueError(f"DataFrame missing required columns: '{group_col}' and '{result_col}'.")
    if len(df[group_col].unique()) != 2:
        raise ValueError("Expected exactly 2 groups (A and B) in the data.")

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

def calculate_proportion_confidence_interval(successes, total, confidence=0.95):
    """
    Calculate confidence interval for proportions using Wilson score method.
    :param successes: Number of successes
    :param total: Total sample size
    :param confidence: Confidence level
    :return: Tuple containing lower and upper bounds
    """
    proportion = successes / total
    z = stats.norm.ppf((1 + confidence) / 2)
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    margin = z * np.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2)) / denominator
    return center - margin, center + margin

def perform_t_test(group1, group2):
    """
    Perform an independent samples t-test between two groups.
    :param group1: Results of the first group
    :param group2: Results of the second group
    :return: t-statistic, p-value, and effect size (Cohen's d)
    """
    t_stat, p_value = stats.ttest_ind(group1, group2)
    
    # Calculate Cohen's d
    mean1, mean2 = np.mean(group1), np.mean(group2)
    std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    pooled_std = np.sqrt(((len(group1) - 1) * std1**2 + (len(group2) - 1) * std2**2) / (len(group1) + len(group2) - 2))
    cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
    
    return t_stat, p_value, cohens_d

def perform_chi_square_test(df, group_col='group', result_col='result'):
    """
    Perform a chi-square test for categorical data.
    :param df: DataFrame containing the experiment data
    :param group_col: Name of the group column
    :param result_col: Name of the result/conversion column
    :return: chi-square statistic, p-value, contingency table
    """
    contingency_table = pd.crosstab(df[group_col], df[result_col])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    return chi2, p_value, contingency_table, expected

def detect_data_type(df, result_col='result'):
    """
    Detect if the result column is continuous or categorical.
    :param df: DataFrame containing the experiment data
    :param result_col: Name of the result column
    :return: 'categorical' or 'continuous'
    """
    unique_values = df[result_col].nunique()
    total_rows = len(df)
    
    # If less than 10% unique values or all binary, treat as categorical
    if unique_values <= 2 or unique_values / total_rows < 0.1:
        return 'categorical'
    return 'continuous'

def generate_summary_statistics(df, group_col='group', result_col='result'):
    """
    Generate detailed summary statistics for each group.
    :param df: DataFrame containing the experiment data
    :param group_col: Name of the group column
    :param result_col: Name of the result column
    :return: Dictionary containing summary statistics
    """
    summary = {}
    
    for group in df[group_col].unique():
        group_data = df[df[group_col] == group][result_col]
        summary[group] = {
            'count': len(group_data),
            'mean': group_data.mean(),
            'median': group_data.median(),
            'std': group_data.std(),
            'min': group_data.min(),
            'max': group_data.max(),
            '25%': group_data.quantile(0.25),
            '75%': group_data.quantile(0.75)
        }
    
    return summary

def create_visualizations(df, group_col='group', result_col='result', output_dir='results'):
    """
    Create visualization plots for the A/B test results.
    :param df: DataFrame containing the experiment data
    :param group_col: Name of the group column
    :param result_col: Name of the result column
    :param output_dir: Directory to save visualizations
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    data_type = detect_data_type(df, result_col)
    
    # Create a figure with multiple subplots
    if data_type == 'categorical':
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Conversion rate bar plot
        conversion_rates = df.groupby(group_col)[result_col].mean()
        conversion_rates.plot(kind='bar', ax=axes[0], color=['#3498db', '#e74c3c'])
        axes[0].set_title('Conversion Rate by Group', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Conversion Rate')
        axes[0].set_xlabel('Group')
        axes[0].set_ylim(0, 1)
        
        # Contingency table heatmap
        contingency = pd.crosstab(df[group_col], df[result_col])
        sns.heatmap(contingency, annot=True, fmt='d', cmap='YlOrRd', ax=axes[1], cbar_kws={'label': 'Count'})
        axes[1].set_title('Contingency Table', fontsize=14, fontweight='bold')
    else:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Box plot
        df.boxplot(column=result_col, by=group_col, ax=axes[0])
        axes[0].set_title('Distribution by Group (Box Plot)', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Value')
        axes[0].set_xlabel('Group')
        plt.sca(axes[0])
        plt.xticks(rotation=0)
        
        # Histogram
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group][result_col]
            axes[1].hist(group_data, alpha=0.6, label=f'Group {group}', bins=20)
        axes[1].set_title('Distribution by Group (Histogram)', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Value')
        axes[1].set_ylabel('Frequency')
        axes[1].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ab_test_visualizations.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Visualizations saved to '{output_dir}/ab_test_visualizations.png'")
    plt.close()

def generate_report(df, config, group_col='group', result_col='result', output_dir='results'):
    """
    Generate a comprehensive A/B test report.
    :param df: DataFrame containing the experiment data
    :param config: Configuration dictionary
    :param group_col: Name of the group column
    :param result_col: Name of the result column
    :param output_dir: Directory to save the report
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    confidence = config.get('confidence_level', 0.95)
    significance = config.get('significance_threshold', 0.05)
    
    # Validate data
    try:
        validate_data(df, group_col, result_col)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Detect data type
    data_type = detect_data_type(df, result_col)
    
    # Generate summary statistics
    summary = generate_summary_statistics(df, group_col, result_col)
    
    # Prepare report
    report = []
    report.append("=" * 60)
    report.append("A/B TEST ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"\nData Type Detected: {data_type.upper()}")
    report.append(f"Confidence Level: {confidence * 100}%")
    report.append(f"Significance Threshold: {significance}")
    report.append(f"\n{'GROUP SUMMARY STATISTICS':-^60}")
    report.append("-" * 60)
    
    for group, stats_dict in summary.items():
        report.append(f"\nGroup {group}:")
        report.append(f"  Sample Size:  {stats_dict['count']}")
        report.append(f"  Mean:         {stats_dict['mean']:.4f}")
        report.append(f"  Median:       {stats_dict['median']:.4f}")
        report.append(f"  Std Dev:      {stats_dict['std']:.4f}")
        report.append(f"  Min:          {stats_dict['min']:.4f}")
        report.append(f"  Max:          {stats_dict['max']:.4f}")
        report.append(f"  Q1 (25%):     {stats_dict['25%']:.4f}")
        report.append(f"  Q3 (75%):     {stats_dict['75%']:.4f}")
    
    report.append(f"\n{'STATISTICAL TEST RESULTS':-^60}")
    report.append("-" * 60)
    
    if data_type == 'categorical':
        chi2, p_value, contingency, expected = perform_chi_square_test(df, group_col, result_col)
        report.append(f"\nChi-Square Test (Categorical Data):")
        report.append(f"  Chi-Square Statistic: {chi2:.4f}")
        report.append(f"  P-value:              {p_value:.6f}")
        report.append(f"\nContingency Table:")
        report.append(f"{contingency.to_string()}")
        
        # Calculate conversion rates and confidence intervals
        report.append(f"\nConversion Rates with {confidence * 100}% CI:")
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group]
            conversions = (group_data[result_col] == 1).sum() if result_col in group_data.columns else group_data[result_col].sum()
            total = len(group_data)
            rate = conversions / total
            ci_lower, ci_upper = calculate_proportion_confidence_interval(conversions, total, confidence)
            report.append(f"  Group {group}: {rate:.4f} (95% CI: [{ci_lower:.4f}, {ci_upper:.4f}])")
        
        if p_value < significance:
            report.append(f"\n✓ STATISTICALLY SIGNIFICANT difference detected (p < {significance})")
        else:
            report.append(f"\n✗ NO statistically significant difference (p >= {significance})")
    else:
        group_a = df[df[group_col] == df[group_col].unique()[0]][result_col]
        group_b = df[df[group_col] == df[group_col].unique()[1]][result_col]
        
        t_stat, p_value, cohens_d = perform_t_test(group_a, group_b)
        ci_a = calculate_confidence_interval(group_a, confidence)
        ci_b = calculate_confidence_interval(group_b, confidence)
        
        report.append(f"\nIndependent Samples T-Test (Continuous Data):")
        report.append(f"  T-Statistic:  {t_stat:.4f}")
        report.append(f"  P-value:      {p_value:.6f}")
        report.append(f"  Cohen's d:    {cohens_d:.4f}")
        report.append(f"\nMean with {confidence * 100}% CI:")
        report.append(f"  Group A: {group_a.mean():.4f} (95% CI: [{ci_a[0]:.4f}, {ci_a[1]:.4f}])")
        report.append(f"  Group B: {group_b.mean():.4f} (95% CI: [{ci_b[0]:.4f}, {ci_b[1]:.4f}])")
        
        if p_value < significance:
            report.append(f"\n✓ STATISTICALLY SIGNIFICANT difference detected (p < {significance})")
        else:
            report.append(f"\n✗ NO statistically significant difference (p >= {significance})")
    
    report.append("\n" + "=" * 60)
    
    # Print and save report
    report_text = "\n".join(report)
    print(report_text)
    
    with open(os.path.join(output_dir, 'ab_test_report.txt'), 'w') as f:
        f.write(report_text)
    print(f"\n✓ Report saved to '{output_dir}/ab_test_report.txt'")

def main():
    """
    Main function to run the A/B test analysis.
    """
    parser = argparse.ArgumentParser(description='A/B Test Analysis Tool')
    parser.add_argument('data_file', type=str, help='Path to the CSV file containing experiment data')
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file (default: config.json)')
    parser.add_argument('--group-col', type=str, default='group', help='Name of the group column (default: group)')
    parser.add_argument('--result-col', type=str, default='result', help='Name of the result column (default: result)')
    parser.add_argument('--output-dir', type=str, default='results', help='Directory to save results (default: results)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if config is None:
        return
    
    # Update output directory from command line if provided
    if args.output_dir != 'results':
        config['output_dir'] = args.output_dir
    
    output_dir = config.get('output_dir', 'results')
    
    # Load data
    try:
        df = pd.read_csv(args.data_file)
        print(f"✓ Data loaded successfully from '{args.data_file}'")
    except FileNotFoundError:
        print(f"Error: Data file '{args.data_file}' not found.")
        return
    except pd.errors.ParserError:
        print(f"Error: Unable to parse '{args.data_file}'. Ensure it's a valid CSV file.")
        return
    
    # Generate report and visualizations
    print("\nGenerating A/B test analysis...")
    generate_report(df, config, args.group_col, args.result_col, output_dir)
    create_visualizations(df, args.group_col, args.result_col, output_dir)
    print("\n✓ Analysis complete!")

if __name__ == "__main__":
    main()
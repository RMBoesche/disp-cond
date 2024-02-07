import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('./resultados_ams53psL53.csv')

# Define weights for each measurement (column)
weights = {
    'tplh':                 1,
    'tphl':                 1,
    'trise':                1,
    'tfall':                1,
    'avgp':                 1,
    'avgp_rise':            1,
    'avgp_fall':            1,
    'avgp_leakage_out_1':   1,
    'avgp_leakage_out_0':   1,
    'tp_avg':               9  # New column added to the weights
}

# Create a new DataFrame to store the order of each run in each column
order_df = pd.DataFrame(index=df.index)

# Convert numbers in scientific notation to floats and take absolute values
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col].astype(str).apply(lambda x: float(x.replace('E', 'e'))), errors='coerce').abs()

# Add a new column 'tp_avg' as the average of 'tplh' and 'tphl'
df['tp_avg'] = df[['tplh', 'tphl']].mean(axis=1)

# Calculate points for each column based on the order of runs (reversed ranking order)
for col in df.columns[1:]:
    order_df[col] = df[col].rank(ascending=True, method='min').astype(int)

# Calculate the weighted sum of points for each run
df['score'] = (order_df * pd.Series(weights)).sum(axis=1)

# Sort the DataFrame based on the 'score' column in ascending order
df_sorted = df.sort_values(by='score')

# Calculate percentage deviation from the best run for tp_avg and avgp
best_run_tp_avg = df_sorted['tp_avg'].iloc[0]
best_run_avgp = df_sorted['avgp'].iloc[0]

df_sorted['tp_avg_d'] = ((df_sorted['tp_avg'] - best_run_tp_avg) / best_run_tp_avg) * 100
df_sorted['avgp_d'] = ((df_sorted['avgp'] - best_run_avgp) / best_run_avgp) * 100

# Save the sorted DataFrame to a CSV file
df_sorted.to_csv('results_with_scores_and_deviation.csv', index=False)

# Display the sorted DataFrame with deviation percentages
print(df_sorted[['name_of_run', 'score', 'tp_avg_d', 'avgp_d']].assign(
    tp_avg_d=lambda x: x['tp_avg_d'].map('{:.2f}%'.format),
    avgp_d=lambda x: x['avgp_d'].map('{:.2f}%'.format)
))

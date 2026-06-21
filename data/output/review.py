import pandas as pd

df = pd.read_csv('priority_ny_funders.csv')

print(f'Total rows: {len(df):,}')

print(f'Total columns: {len(df.columns)}')

print('\nColumns in the file: ')

print(df.columns.tolist())

#exporting to excel
df.to_excel('priority_ny_funders_review.xlsx', index=False)

print("\n Successfully exported to 'priority_ny_funders_review.xlsx'")


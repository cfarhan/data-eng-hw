import pandas as pd
from us_state_abbrev import abbrev_to_us_state
import seaborn as sns
import matplotlib.pyplot as plt

# Create dataframes from csv files
cases_df = pd.read_csv('covid_confirmed_usafacts.csv')
deaths_df = pd.read_csv('covid_deaths_usafacts.csv')
census_df = pd.read_csv('acs2017_county_data.csv')

# Trim dataframes
cases_df = cases_df[['County Name', 'State', '2023-07-23']]
deaths_df = deaths_df[['County Name', 'State', '2023-07-23']]
census_df = census_df[['County', 'State', 'TotalPop', 'IncomePerCap', 'Poverty', 'Unemployment']]

print(f'cases_df columns: {cases_df.columns}')
print(f'deaths_df columns: {deaths_df.columns}')
print(f'census_df columns: {census_df.columns}')

cases_df['County Name'] = cases_df['County Name'].str.strip()
deaths_df['County Name'] = deaths_df['County Name'].str.strip()

# Count 'Washington County' appearences
cases_count = (cases_df['County Name'] == 'Washington County').sum()
deaths_count = (deaths_df['County Name'] == 'Washington County').sum()

print(f"'Washington County' in cases_df: {cases_count}")
print(f"'Washington County' in deaths_df: {deaths_count}")

cases_df = cases_df[cases_df['County Name'] != 'Statewide Unallocated']
deaths_df = deaths_df[deaths_df['County Name'] != 'Statewide Unallocated']

print(f'Number of rows in cases_df: {len(cases_df)}')
print(f'Number of rows in deaths_df: {len(deaths_df)}')

# Convert State abbreviations to full names
cases_df['State'] = cases_df['State'].map(abbrev_to_us_state)
deaths_df['State'] = deaths_df['State'].map(abbrev_to_us_state)

print(cases_df.head())

# Create key columns in each DataFrame by combining County and State
cases_df['key'] = cases_df['County Name'] + ', ' + cases_df['State']
deaths_df['key'] = deaths_df['County Name'] + ', ' + deaths_df['State']
census_df['key'] = census_df['County'] + ', ' + census_df['State']

# Set 'key' as the index in each DataFrame
cases_df = cases_df.set_index('key')
deaths_df = deaths_df.set_index('key')
census_df = census_df.set_index('key')

print(f'census_df after setting key to index:\n {census_df.head()}')

# Rename columns
cases_df.rename(columns={'2023-07-23': 'Cases'}, inplace=True)
deaths_df.rename(columns={'2023-07-23': 'Deaths'}, inplace=True)

# Show updated column headers
print("cases_df columns:", cases_df.columns.values.tolist())
print("deaths_df columns:", deaths_df.columns.values.tolist())

# Join cases_df and deaths_df
join_df = cases_df.join(deaths_df[['Deaths']], how='inner')

# Drop the duplicate state column
census_df = census_df.drop(columns=['State'])

# Join the result with census_df
join_df = join_df.join(census_df, how='inner')

print(f'join_df: \n {join_df.head()}')
print(f'Number of rows in join_df: {len(join_df)}')

# Select only numeric columns
numeric_df = join_df.select_dtypes(include='number')

correlation_matrix = numeric_df.corr()
print(correlation_matrix)

sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correleation Matrix Heatmap')
plt.show()
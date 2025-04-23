import csv
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def validate_name(name):
    return bool(name.strip())

def validate_hire_year(hire_date):
    try:
        hire_year = datetime.strptime(hire_date, "%Y-%m-%d").year
        return hire_year >= 2015
    except ValueError:
        return False
    
def validate_birth_before_hire(birth_date, hire_date):
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        hire = datetime.strptime(hire_date, "%Y-%m-%d")
        return birth < hire
    except ValueError:
        return False

def validate_csv_entries(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            entries = list(csv_reader)
            return entries
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def validate_multiple_employees_in_city(city, city_counter):
    return city_counter[city] > 1

def validate_salary_normality(salaries):
    # Create histogram
    plt.hist(salaries, bins=20, edgecolor='black')
    plt.title("Histogram of Salaries")
    plt.xlabel("Salary")
    plt.ylabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    plt.show()

csv_file_path = 'employees.csv'
csv_data = validate_csv_entries(csv_file_path)

nullNames = 0 
invalid_hire_dates = 0
birth_after_hire = 0
city_employees_violations = 0
salaries = []

# Track number of employees in each city
city_counter = Counter()

if csv_data:
    for row in csv_data:
        # Count the employees in each city
        city_counter[row['city']] += 1

        # Validate assertions
        if not validate_name(row['name']):
            nullNames += 1
        if not validate_hire_year(row['hire_date']):
            invalid_hire_dates += 1
        if not validate_birth_before_hire(row['birth_date'], row['hire_date']):
            birth_after_hire += 1
        
        # Collect salaries for normality check
        salary = float(row['salary'])
        salaries.append(salary)

    # Check number of employees in each city violations
    for city, count in city_counter.items():
        if count <= 1:
            city_employees_violations += 1

    # Validate salary normality
    if salaries:
        validate_salary_normality(salaries)

else:
    print("No data to display.")

print(f"Number of records with NULL names: {nullNames}")
print(f"Number of employees hired before 2015: {invalid_hire_dates}")
print(f"Number of employees born after or on hire date: {birth_after_hire}")
print(f"Number of cities with fewer than two employees: {city_employees_violations}")

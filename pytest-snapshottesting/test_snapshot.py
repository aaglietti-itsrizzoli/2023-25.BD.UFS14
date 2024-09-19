import csv
from CsvTextBuilder import CsvTextBuilder

def func(x):
    return x + 1

def test_answer(snapshot):
    extract_ouput = func(23)
    snapshot.snapshot_dir = 'snapshots'  # This line is optional.
    snapshot.assert_match(str(extract_ouput), 'foo_output.txt')

def func_csv():
    csvfile = CsvTextBuilder()
    data = [['Name', 'Age', 'Salary'], ['Bob', '45', '75000'], ['Andrew', '34', '79000']]
    writer = csv.writer(csvfile, lineterminator='\n')
    writer.writerows(data)
    csv_string = csvfile.csv_string
    csv_string_formatted = ''.join(csv_string)
    return csv_string_formatted

def test_func_csv(snapshot):
    csv_ouput = func_csv()
    snapshot.snapshot_dir = 'snapshots'  # This line is optional.
    snapshot.assert_match(csv_ouput, 'func_csv_output.csv')

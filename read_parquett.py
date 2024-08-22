import pandas as pd

# Replace 'your_file.parquet' with the path to your actual Parquet file
file_path = '/CMFX_RAW/tests/interferometer/CMFX_00036_scope_24_param.parquet'

# Read the Parquet file into a pandas DataFrame
df = pd.read_parquet(file_path)

# Display the contents of the DataFrame
print("Contents of the Parquet file:")
print(df)
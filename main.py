from src.preprocessing import choose_file, preprocess_dataset #importing necessary functions
import pandas as pd

print("Select a text file to clean...")
file_path = choose_file()

print("You selected:", file_path)

# Read the file
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read() #reading the selected file

# Put into dataframe
df = pd.DataFrame({"text": [text]})

# Clean it
cleaned = preprocess_dataset(df)["clean_text"][0] #applying preprocessing to get cleaned text

# Show results
print("\nOriginal Text:\n")
print(text)

print("\nCleaned Text:\n")
print(cleaned)
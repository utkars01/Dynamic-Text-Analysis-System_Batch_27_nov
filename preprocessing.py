import re #importing regular expressions module
import pandas as pd #importing pandas for data manipulation
import spacy #importing spacy for NLP tasks
from tkinter import Tk, filedialog #importing tkinter for file dialog
from datasets import load_dataset #importing load_dataset from datasets library
import os #importing os for file operations

nlp = spacy.load("en_core_web_sm") #loading small english model from spacy

CUSTOM_STOPWORDS={"movie","film","watch","like","good","bad",
    "story","character","time","people","scene",
    "director","show"}

def choose_file():
    Tk().withdraw()   # Hide the small Tkinter window
    file_path = filedialog.askopenfilename( #opening file dialog to select a text file
        title="Select a text file", #dialog title
        filetypes=[("Text Files", "*.txt")] #file types filter
    )
    return file_path #returning selected file path


def load_imdb_rottentomatoes():
    imdb=load_dataset("imdb") #loading imdb dataset
    imdb_df=pd.DataFrame(imdb['train'])[["text"]] #converting train split to dataframe
    rt=load_dataset("rotten_tomatoes") #loading rotten tomatoes dataset
    rt_df=pd.DataFrame(rt['train'])[["text"]] #converting train split to dataframe
    combined_df=pd.concat([imdb_df,rt_df],ignore_index=True) #combining both dataframes
    combined_df["text"]=combined_df["text"].fillna("") # text column is string type
    return combined_df

def load_imdb_with_labels():
     imdb=load_dataset("imdb") #loading imdb dataset
     train_df=pd.DataFrame(imdb['train'])[["text","label"]] #converting train split to dataframe
     test_df=pd.DataFrame(imdb['test'])[["text","label"]] #converting

     df=pd.concat([train_df,test_df],ignore_index=True) #combining both dataframes
     df["text"]=df["text"].fillna("") # text column is string type
     return df #returning combined dataframe

def load_text_files(folder="data"):
    texts = [] #list to hold text contents
    for file in os.listdir(folder): #iterating through files in the folder
        if file.endswith(".txt"): #checking for .txt files
                with open(os.path.join(folder, file), 'r', encoding='utf-8') as f: #opening each text file
                    texts.append(f.read()) #reading and appending content to list
    return texts #returning list of text contents

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # for removing extra whitespace
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Removing URLs
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)  # for removing special characters
    text=text.lower() # converting to lowercase
    document=nlp(text) #processing text with spacy
    tokens=[token.lemma_
            for token in document
            if not token.is_stop
            and token.lemma_ not in CUSTOM_STOPWORDS
            and token.pos_ in {'NOUN','ADJ','VERB'}
            and len(token.lemma_)>2
        ]
    return " ".join(tokens) #joining tokens back to string

def preprocess_dataset(df):
    df['clean_text'] = df['text'].apply(clean_text) # applying cleaning function to each text entry
    return df # returning dataframe with new cleaned text column
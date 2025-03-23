import pandas as pd
import numpy as np
from datetime import datetime
import os
import uuid

class CleanData:
    def __init__(self):
        self.path_id = None
        self.df_id = None
        self.df = None
        self.df_list = {}

    def set_active_df(self, path_id, df_index):
        if self.df is not None:
            # Savepoint for current dataframe
            df_current = {
                'type': 'modified',
                'timestamp': datetime.now(),
                'data': self.df.copy()  # Ensure no reference issues
            }

            history = self.df_list[self.path_id]['history']
            new_df_id = len(history)

            history[new_df_id] = df_current

        self.path_id = path_id
        self.df_index = df_index
        self.df = self.df_list[path_id]['history'][df_index]['data']

    def load_csv(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        path_id = str(uuid.uuid4())  # Unique identifier for dataset
        df_history = []

        try:
            df_new = pd.read_csv(path)
            if df_new.empty:
                print(f"Warning: The CSV {path} is empty.")
        except Exception as e:
            raise ValueError(f"Error reading CSV {path}: {e}")

        metadata = {
            'source': path,
            'loaded_at': datetime.now(),
        }

        df_current = {
            'type': 'raw',
            'timestamp': datetime.now(),
            'data': df_new
        }

        df_history.append(df_current) 

        self.df_list[path_id] = {
            'metadata': metadata,
            'history': df_history
        }

        self.set_active_df(path_id, df_index=0)

    def add_col(self, name, formula):
        """Adds a new column based on a user-provided formula."""
        try:
            # Replace brackets with proper pandas column references
            formula = formula.replace("[", "").replace("]", "")

            # Use pandas.eval() for a safer execution
            # self.df[name] = pd.eval(calc, local_dict=self.df.to_dict("series"))
            self.df[name] = pd.eval(formula, local_dict=self.df.to_dict("series"))

            # st.success(f"✅ Column '{name}' added successfully!")
        except Exception as e:
            pass
            # st.error(f"❌ Error applying formula: {e}")

    def filter_rows(self, filter_dict):
        """Filters rows based on user-defined conditions."""
        try:
            query_list = [f"`{col}` {expr}" for col, expr in filter_dict.items()]
            query_string = " & ".join(query_list)
            self.df = self.df.query(query_string)
            # st.success("✅ Data filtered successfully!")
        except Exception as e:
            pass
            # st.error(f"❌ Error filtering data: {e}")
            
    def remove_duplicates(self):
        if self.df is not None:
            self.df.drop_duplicates(inplace=True)

    def merge_csv(self, df_index, merge_columns):
        merge_df = self.df_list[df_index]
        self.df = pd.concat([self.df, merge_df], ignore_index=True)

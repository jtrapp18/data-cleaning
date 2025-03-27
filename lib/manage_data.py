import pandas as pd
import json
import numpy as np
from datetime import datetime
import os
import uuid
from .config import CONFIG

class ManageData:
    """
    Handles data cleaning and management for a given client and year.
    """
    
    def __init__(self, client: str, year: str) -> None:
        """
        Initializes CleanData with client and year, ensuring directory structure exists.

        Parameters
        ------------
        client: str
            The client name.
        year: str
            The year associated with the data.
        """
        self.client = client
        self.year = year
        self.path_id = None
        self.df_id = None
        self.df_list = {}
        self.df = None
        self.transformations = []

        data_path = CONFIG['paths']['data']

        # Ensure directory structure exists
        self.save_path = f"{data_path}{self.client}/{self.year}/metadata.json"
        self.data_path = f"{data_path}{self.client}/{self.year}/data"
        os.makedirs(self.data_path, exist_ok=True)

        # Load previous state if available
        self.load_state()

    def load_state(self) -> None:
        """
        Load saved progress from a JSON file if it exists.
        """
        if os.path.exists(self.save_path):
            with open(self.save_path, "r") as f:
                metadata = json.load(f)
            
            self.df_list = metadata["df_list"]
            self.set_active_df(path_id=metadata["path_id"],
                               df_index=metadata["df_id"])
            print(f"🔄 Loaded saved data for {self.client} - {self.year}")
        else:
            print(f"🆕 No savepoint found. Starting fresh for {self.client} - {self.year}")

    def add_checkpoint(self, comment: str = "modified") -> None:
        """
        Saves a checkpoint of the current dataframe.

        Parameters
        ------------
        comment: str
            A short description of the checkpoint.
        """
        df_filename = f"{self.path_id}_{len(self.df_list[self.path_id]['history'])}.parquet"
        df_filepath = os.path.join(self.data_path, df_filename)
        
        self.df.to_parquet(df_filepath)
        
        df_current = {
            'comment': comment,
            'timestamp': str(datetime.now()),
            'data_path': df_filename,
            'transformations': self.transformations.copy()
        }
        self.df_list[self.path_id]['history'].append(df_current)
        self.save_state()
    
    def save_state(self) -> None:
        """
        Saves the current state to a JSON file.
        """
        metadata = {
            "client": self.client,
            "year": self.year,
            "last_saved": str(datetime.now()),
            "path_id": self.path_id,
            "df_id": self.df_id,
            "df_list": self.df_list
        }
        with open(self.save_path, "w") as f:
            json.dump(metadata, f, indent=4)
        print(f"✅ Progress saved for {self.client} - {self.year}")

    def set_active_df(self, path_id: str, df_index: int) -> None:
        """
        Sets the active dataframe based on the path_id and index in history.

        Parameters
        ------------
        path_id: str
            Unique identifier for the dataset.
        df_index: int
            The index of the dataframe version to load.
        """
        if self.df is not None:
            self.add_checkpoint()
        
        self.path_id = path_id
        self.df_id = df_index

        df_metadata = self.df_list[path_id]['history'][df_index]
        df_filepath = os.path.join(self.data_path, df_metadata['data_path'])
        self.df = pd.read_parquet(df_filepath)
        self.transformations = df_metadata['transformations']

    def load_csv(self, path: str) -> None:
        """
        Loads a CSV file and saves its initial state.

        Parameters
        ------------
        path: str
            The file path of the CSV to load.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        path_id = str(uuid.uuid4())
        df_history = []
        
        try:
            df_new = pd.read_csv(path)
            if df_new.empty:
                print(f"⚠️ Warning: The CSV {path} is empty.")
        except Exception as e:
            raise ValueError(f"❌ Error reading CSV {path}: {e}")
        
        metadata = {
            'source': path,
            'loaded_at': str(datetime.now()),
        }
        
        df_filename = f"{path_id}_0.parquet"
        df_filepath = os.path.join(self.data_path, df_filename)
        df_new.to_parquet(df_filepath)
        
        df_current = {
            'comment': 'raw',
            'timestamp': str(datetime.now()),
            'data_path': df_filename,
            'transformations': []
        }
        
        df_history.append(df_current)
        
        self.df_list[path_id] = {
            'metadata': metadata,
            'history': df_history
        }
        
        self.set_active_df(path_id, df_index=0)

    def get_active_df_info(self) -> dict:
        """
        Returns metadata about the currently active dataframe.

        Returns
        ------------
        dict: Dictionary containing dataframe metadata.
        """
        if not self.path_id or self.df_id is None:
            return {"message": "No active dataframe."}
        
        metadata = self.df_list[self.path_id]["metadata"]
        return {
            "client": self.client,
            "year": self.year,
            "last_saved": str(datetime.now()),
            "source": metadata["source"],
            "active_dataset": self.path_id,
            "active_version": self.df_id,
            "rows": len(self.df),
            "columns": list(self.df.columns)
        }
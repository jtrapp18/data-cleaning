import pandas as pd
from .manage_data import ManageData

class CleanData(ManageData):
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
        super().__init__(client, year)

    def add_col(self, name: str, formula: str) -> None:
        """
        Adds a new column based on a user-provided formula.

        Parameters
        ------------
        name: str
            The name of the new column.
        formula: str
            A formula to compute values for the new column.
        """
        try:
            # Replace brackets with proper pandas column references
            formula = formula.replace("[", "").replace("]", "")
            self.df[name] = pd.eval(formula, local_dict=self.df.to_dict("series"))

            trans_dict = {
                'name': 'Added Column',
                'column_name': name,
                'formula': formula
            }
            self.transformations.append(trans_dict)

        except Exception as e:
            print(f"❌ Error applying formula: {e}")

    def filter_rows(self, filter_dict: dict) -> None:
        """
        Filters rows based on user-defined conditions.

        Parameters
        ------------
        filter_dict: dict
            Dictionary where keys are column names and values are filter expressions.
        """
        try:
            query_list = [f"{col} {expr}" for col, expr in filter_dict.items()]
            query_string = " & ".join(query_list)
            self.df = self.df.query(query_string)

            trans_dict = {
                'name': 'Filtered Rows',
                'filters': filter_dict
            }
            self.transformations.append(trans_dict)

        except Exception as e:
            print(f"❌ Error filtering data: {e}")

    def remove_duplicates(self) -> None:
        """
        Removes duplicate rows from the active DataFrame.
        """
        if self.df is not None:
            self.df.drop_duplicates(inplace=True)

            trans_dict = {'name': 'Removed Duplicates'}
            self.transformations.append(trans_dict)

    def merge_csv(self, df_index: str, merge_columns: list) -> None:
        """
        Merges the active DataFrame with another DataFrame from the stored history.

        Parameters
        ------------
        df_index: str
            The identifier of the stored DataFrame to merge with.
        merge_columns: list[str]
            List of columns on which to perform the merge.
        """
        if df_index not in self.df_list:
            print(f"❌ Error: No dataset found with ID {df_index}")
            return

        # Load the historical DataFrame
        merge_df = self.df_list[df_index]["history"][-1]["data"]

        try:
            self.df = pd.merge(self.df, merge_df, on=merge_columns, how="outer")
            trans_dict = {'name': 'Merged DataFrame', 'columns': merge_columns}
            self.transformations.append(trans_dict)

        except Exception as e:
            print(f"❌ Error merging datasets: {e}")
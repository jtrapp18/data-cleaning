import os
ROOT = './'

class ClientPath:
    
    def __init__(self, client):
        self.client_root = os.path.join(ROOT, client)
        self.database_root = os.path.join(self.client_root, 'database')
        self.years_root = os.path.join(self.client_root, 'years')
        
        # Ensure the client directory exists
        os.makedirs(self.client_root, exist_ok=True)

    def get(self, section, subsection=None, create=False, **kwargs):
        """Dynamically generate paths based on section, subsection, and optional creation flag."""
        db_name = kwargs.get('db_name', 'default_db')
        spec_name = kwargs.get('spec_name', 'default')
        year = str(kwargs.get('year', 'default'))

        paths = {
            'database': {
                'root': os.path.join(self.database_root, 'database', db_name),
                'data': os.path.join(self.database_root, 'database', db_name, 'data.parquet'),
                'specs': os.path.join(self.database_root, 'database', db_name, 'specs.json'),
            },
            'named_specs': {
                'specs': os.path.join(self.client_root, 'named_specs', spec_name, 'specs.json'),
            },
            'years': {
                'root': os.path.join(self.years_root, year),
                'data': os.path.join(self.years_root, year, 'parsed_data.parquet'),
                'metadata': os.path.join(self.years_root, year, 'metadata.json'),
            }
        }

        # Get the path
        selected_path = paths.get(section, {}).get(subsection) if subsection else paths.get(section)

        # If path exists and creation is enabled, ensure parent directories exist
        if create and selected_path:
            os.makedirs(os.path.dirname(selected_path) if os.path.splitext(selected_path)[1] else selected_path, exist_ok=True)

        return selected_path
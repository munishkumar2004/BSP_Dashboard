import pandas as pd


class DataCleaner:
    def __init__(self, file_path):
        if str(file_path).endswith('.csv'):
            self.df = pd.read_csv(file_path, on_bad_lines='skip')
        else:
            self.df = pd.read_excel(file_path)
        self.original_shape = self.df.shape
        self.actions_performed = []

    def remove_duplicates(self):
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)
        if removed > 0:
            self.actions_performed.append(f"Removed {removed} duplicate rows")
        return removed

    def fill_numeric_missing(self):
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        filled = 0
        for col in numeric_cols:
            missing = self.df[col].isnull().sum()
            if missing > 0:
                self.df[col] = self.df[col].fillna(self.df[col].mean())
                filled += missing
        if filled > 0:
            self.actions_performed.append(f"Filled {filled} numeric missing values with mean")
        return filled

    def fill_text_missing(self):
        text_cols = self.df.select_dtypes(include=['object']).columns
        filled = 0
        for col in text_cols:
            missing = self.df[col].isnull().sum()
            if missing > 0:
                self.df[col] = self.df[col].fillna('Unknown')
                filled += missing
        if filled > 0:
            self.actions_performed.append(f"Filled {filled} text missing values with 'Unknown'")
        return filled

    def drop_missing_rows(self):
        before = len(self.df)
        self.df = self.df.dropna()
        removed = before - len(self.df)
        if removed > 0:
            self.actions_performed.append(f"Dropped {removed} rows with missing values")
        return removed

    def get_report(self):
        return {
            'original_rows': self.original_shape[0],
            'original_columns': self.original_shape[1],
            'final_rows': len(self.df),
            'final_columns': len(self.df.columns),
            'actions_performed': self.actions_performed
        }
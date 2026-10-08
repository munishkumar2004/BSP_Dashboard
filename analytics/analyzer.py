import pandas as pd
import plotly.express as px
import plotly.io as pio


class DataAnalyzer:
    def __init__(self, file_path):
        if str(file_path).endswith('.csv'):
            self.df = pd.read_csv(file_path)
        else:
            self.df = pd.read_excel(file_path)

    def get_summary(self):
        return self.df.describe().to_dict()

    def get_head(self):
        # 🟢 Bootstrap classes add ki gayi hain, taaki table professional dikhe
        return self.df.iloc[:, :15].head().to_html(
            classes='table table-striped table-bordered table-hover',
            border=0,
            justify='left'
        )

    def get_columns(self):
        cols = list(self.df.columns)
        if len(cols) > 15:
            return cols[:15] + [f"... aur {len(cols) - 15} columns"]
        return cols

    def get_chart(self):
        numeric_df = self.df.select_dtypes(include=['number'])
        if len(numeric_df.columns) >= 2:
            fig = px.scatter(
                numeric_df,
                x=numeric_df.columns[0],
                y=numeric_df.columns[1],
                title="Scatter Plot"
            )
            return pio.to_html(fig, full_html=False)
        return None

    def get_time_series_chart(self):
        date_cols = []
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                try:
                    pd.to_datetime(self.df[col], errors='raise')
                    date_cols.append(col)
                except:
                    pass

        if not date_cols:
            return None

        date_col = date_cols[0]
        numeric_cols = list(self.df.select_dtypes(include=['number']).columns)

        if not numeric_cols:
            return None

        try:
            df_copy = self.df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            df_copy = df_copy.dropna(subset=[date_col])
            df_copy = df_copy.sort_values(date_col)

            fig = px.line(
                df_copy,
                x=date_col,
                y=numeric_cols[0],
                title=f"{numeric_cols[0]} Trend over {date_col}"
            )
            return pio.to_html(fig, full_html=False)
        except:
            return None

    def get_correlation_heatmap(self):
        numeric_df = self.df.select_dtypes(include=['number'])
        if len(numeric_df.columns) < 2:
            return None
        try:
            corr = numeric_df.corr()
            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                title="Correlation Heatmap",
                color_continuous_scale='RdBu_r'
            )
            return pio.to_html(fig, full_html=False)
        except:
            return None

    def get_data_quality(self):
        total_cells = self.df.shape[0] * self.df.shape[1]
        missing_cells = int(self.df.isnull().sum().sum())
        missing_pct = round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0

        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': missing_cells,
            'missing_percentage': missing_pct,
            'duplicate_rows': int(self.df.duplicated().sum()),
            'quality_score': round(100 - missing_pct, 2)
        }
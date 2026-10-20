import pandas as pd
import plotly.express as px
import plotly.io as pio


class DataAnalyzer:
    def __init__(self, file_path):
        if str(file_path).endswith('.csv'):
            self.df = pd.read_csv(file_path, on_bad_lines='skip')
        else:
            self.df = pd.read_excel(file_path)

    def get_summary(self):
        return self.df.describe().to_dict()

    def get_head(self):
        df_head = self.df.iloc[:, :15].head().copy()
        df_head.index = df_head.index + 1
        return df_head.to_html(
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

    def get_text_analysis(self):
        text_cols = []
        for col in self.df.columns:
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                is_date = False
                try:
                    pd.to_datetime(self.df[col].dropna().head(10), errors='raise')
                    is_date = True
                except:
                    pass
                if not is_date:
                    text_cols.append(col)

        if not text_cols:
            return None

        col = text_cols[0]
        value_counts = self.df[col].value_counts().head(10)

        try:
            fig_pie = px.pie(
                values=value_counts.values,
                names=value_counts.index.astype(str),
                title=f"Top Categories in '{col}'"
            )
            pie_html = pio.to_html(fig_pie, full_html=False)

            fig_bar = px.bar(
                x=value_counts.index.astype(str),
                y=value_counts.values,
                title=f"Frequency of '{col}'",
                labels={'x': col, 'y': 'Count'}
            )
            bar_html = pio.to_html(fig_bar, full_html=False)

            return {
                'column_name': col,
                'pie_chart': pie_html,
                'bar_chart': bar_html,
                'top_values': dict(value_counts),
                'total_unique': int(self.df[col].nunique())
            }
        except:
            return None

    def get_popularity_vs_danceability_chart(self):
        if 'popularity' in self.df.columns and 'danceability' in self.df.columns:
            try:
                df_sample = self.df.sample(n=min(2000, len(self.df)), random_state=42)
                fig = px.scatter(
                    df_sample,
                    x='danceability',
                    y='popularity',
                    color='track_genre' if 'track_genre' in df_sample.columns else None,
                    title='Popularity vs Danceability (Sample of 2000 tracks)'
                )
                return pio.to_html(fig, full_html=False)
            except Exception:
                return None
        return None
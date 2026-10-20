import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, accuracy_score
from xgboost import XGBClassifier, XGBRegressor


class ModelTrainer:
    def __init__(self, file_path):
        if str(file_path).endswith('.csv'):
            self.df = pd.read_csv(file_path, on_bad_lines='skip')
        else:
            self.df = pd.read_excel(file_path)

    def preprocess(self):
        """Text columns ko numbers mein convert karo aur missing values bharo"""
        df = self.df.copy()
        
        # Numeric check using pandas API
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna('Unknown')
        
        # Text columns ko numbers mein convert karo
        label_encoders = {}
        for col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
        
        return df

    def train(self):
        df = self.preprocess()
        
        if len(df.columns) < 2:
            return None, "Kam se kam 2 columns chahiye."
        
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        unique_values = y.nunique()
        
        if unique_values <= 10:
            algorithms = {
                'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss'),
                'Logistic Regression': LogisticRegression(max_iter=5000)
            }
            problem_type = "Classification"
            metric_name = "Accuracy"
        else:
            algorithms = {
                'Linear Regression': LinearRegression(),
                'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'XGBoost': XGBRegressor(n_estimators=100, random_state=42)
            }
            problem_type = "Regression"
            metric_name = "R2 Score"
        
        best_model = None
        best_score = -999
        best_algo_name = ""
        all_results = {}
        
        for name, model in algorithms.items():
            try:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
                if problem_type == "Classification":
                    score = accuracy_score(y_test, preds)
                else:
                    score = r2_score(y_test, preds)
                
                all_results[name] = round(score, 4)
                
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_algo_name = name
            except Exception as e:
                all_results[name] = f"Failed: {str(e)[:50]}"
        
        os.makedirs('media/models', exist_ok=True)
        joblib.dump(best_model, 'media/models/latest_model.pkl')
        
        feature_importance = {}
        try:
            if hasattr(best_model, 'feature_importances_'):
                importance = best_model.feature_importances_
                feature_importance = dict(zip(X.columns, [round(float(i), 4) for i in importance]))
                feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        except:
            pass
        
        result = {
            'best_algorithm': best_algo_name,
            'best_score': round(best_score, 4),
            'problem_type': problem_type,
            'metric_name': metric_name,
            'all_results': all_results,
            'feature_importance': feature_importance
        }
        
        return result, None
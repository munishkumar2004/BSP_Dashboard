from django.test import TestCase
from ml_engine.trainer import ModelTrainer
import os
import tempfile
import pandas as pd


def create_ml_test_csv():
    """ML training ke liye test CSV banata hai (regression)"""
    data = {
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 22, 28, 33, 38, 43, 48, 53],
        'experience': [2, 5, 8, 12, 15, 18, 22, 25, 1, 4, 6, 10, 14, 17, 20],
        'salary': [
            30000, 45000, 60000, 80000, 95000,
            110000, 125000, 140000, 25000, 40000,
            52000, 68000, 87000, 102000, 118000
        ],
    }
    df = pd.DataFrame(data)

    temp_file = tempfile.NamedTemporaryFile(
        mode='w', suffix='.csv', delete=False, newline=''
    )
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name


class ModelTrainerTestCase(TestCase):
    """Test ML ModelTrainer class"""

    def setUp(self):
        self.csv_path = create_ml_test_csv()

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    def test_trainer_loads_data(self):
        """CSV load ho raha hai?"""
        trainer = ModelTrainer(self.csv_path)
        self.assertEqual(len(trainer.df), 15)

    def test_train_returns_result(self):
        """Model train ho raha hai aur result deta hai?"""
        trainer = ModelTrainer(self.csv_path)
        result, error = trainer.train()
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('best_algorithm', result)
        self.assertIn('best_score', result)
        self.assertIn('problem_type', result)

    def test_train_detects_regression(self):
        """Regression problem detect ho raha hai?"""
        trainer = ModelTrainer(self.csv_path)
        result, error = trainer.train()
        # 15 unique salary values hain, toh regression hoga
        self.assertEqual(result['problem_type'], 'Regression')

    def test_feature_importance(self):
        """Feature importance calculate ho rahi hai?"""
        trainer = ModelTrainer(self.csv_path)
        result, error = trainer.train()
        self.assertIn('feature_importance', result)
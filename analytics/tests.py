from django.test import TestCase
from analytics.analyzer import DataAnalyzer
from analytics.cleaner import DataCleaner
import os
import tempfile
import pandas as pd


def create_test_csv():
    """Ek temporary CSV file banata hai testing ke liye"""
    data = {
        'name': ['Munish', 'Raj', 'Priya', 'Munish', 'Ankit'],
        'age': [25, 30, None, 25, 35],
        'salary': [30000, 45000, 50000, 30000, None],
        'city': ['Bhilai', 'Raipur', 'Durg', 'Bhilai', 'Bhilai'],
    }
    df = pd.DataFrame(data)

    temp_file = tempfile.NamedTemporaryFile(
        mode='w', suffix='.csv', delete=False, newline=''
    )
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name


class DataAnalyzerTestCase(TestCase):
    """Test DataAnalyzer class"""

    def setUp(self):
        self.csv_path = create_test_csv()
        self.analyzer = DataAnalyzer(self.csv_path)

    def tearDown(self):
        """Test ke baad temp file delete karo"""
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    def test_analyzer_loads_data(self):
        """CSV load ho raha hai?"""
        self.assertEqual(len(self.analyzer.df), 5)
        self.assertEqual(len(self.analyzer.df.columns), 4)

    def test_get_head(self):
        """Head function kaam kar raha hai?"""
        head = self.analyzer.get_head()
        self.assertIn('<table', head)
        self.assertIn('Munish', head)

    def test_get_columns(self):
        """Columns nikle hain?"""
        cols = self.analyzer.get_columns()
        self.assertIn('name', cols)
        self.assertIn('age', cols)
        self.assertIn('salary', cols)

    def test_get_data_quality(self):
        """Data quality metrics sahi hain?"""
        quality = self.analyzer.get_data_quality()
        self.assertEqual(quality['total_rows'], 5)
        self.assertEqual(quality['total_columns'], 4)
        self.assertGreater(quality['missing_values'], 0)
        self.assertGreater(quality['duplicate_rows'], 0)

    def test_get_chart(self):
        """Scatter plot generate ho raha hai?"""
        chart = self.analyzer.get_chart()
        # 2 numeric columns hain (age, salary), toh chart banega
        self.assertIsNotNone(chart)

    def test_get_text_analysis(self):
        """Text analysis kaam kar raha hai?"""
        text_analysis = self.analyzer.get_text_analysis()
        self.assertIsNotNone(text_analysis)
        self.assertIn('column_name', text_analysis)


class DataCleanerTestCase(TestCase):
    """Test DataCleaner class"""

    def setUp(self):
        self.csv_path = create_test_csv()

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    def test_remove_duplicates(self):
        """Duplicate rows remove ho rahe hain?"""
        cleaner = DataCleaner(self.csv_path)
        before = len(cleaner.df)
        removed = cleaner.remove_duplicates()
        after = len(cleaner.df)
        self.assertLess(after, before)
        self.assertGreater(removed, 0)

    def test_fill_numeric_missing(self):
        """Numeric missing values fill ho rahi hain?"""
        cleaner = DataCleaner(self.csv_path)
        filled = cleaner.fill_numeric_missing()
        self.assertGreater(filled, 0)
        # Ab koi missing value nahi honi chahiye numeric columns mein
        numeric_cols = cleaner.df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            self.assertEqual(cleaner.df[col].isnull().sum(), 0)

    def test_fill_text_missing(self):
        """Text missing values 'Unknown' se fill ho rahi hain?"""
        cleaner = DataCleaner(self.csv_path)
        filled = cleaner.fill_text_missing()
        self.assertGreaterEqual(filled, 0)

    def test_get_report(self):
        """Cleaner report banata hai?"""
        cleaner = DataCleaner(self.csv_path)
        cleaner.remove_duplicates()
        report = cleaner.get_report()
        self.assertIn('original_rows', report)
        self.assertIn('final_rows', report)
        self.assertIn('actions_performed', report)
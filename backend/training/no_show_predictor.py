"""
HealthConnect AI - No-Show Prediction Model Training
=====================================================
Trains a classification model to predict appointment no-shows.

Auto-detects the target column and features from the dataset.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
)
import joblib

from config.logging_config import get_logger

logger = get_logger(__name__)


class NoShowPredictor:
    """Trains a no-show prediction model for HealthConnect Clinic."""
    
    def __init__(self, data_path: str = "data/raw/HealthConnect_Appointment_Data.csv"):
        self.data_path = Path(data_path)
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.feature_columns = []
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.target_column = None
        
        logger.info(f"NoShowPredictor initialized with data: {data_path}")
    
    def load_data(self) -> pd.DataFrame:
        """Load and inspect the appointment dataset"""
        self.df = pd.read_csv(self.data_path)
        logger.info(f"Loaded {len(self.df)} appointment records")
        logger.info(f"Columns: {self.df.columns.tolist()}")
        
        # Auto-detect target column
        self.target_column = self._detect_target_column()
        logger.info(f"Detected target column: {self.target_column}")
        
        return self.df
    
    def _detect_target_column(self) -> str:
        """Auto-detect the target column (no-show indicator)"""
        target_candidates = [
            'no_show', 'no-show', 'No-show', 'No_Show', 'noShow',
            'no_show_status', 'attended', 'outcome', 'status',
            'appointment_outcome',
        ]
        
        for col in self.df.columns:
            col_lower = col.lower().replace('-', '_').replace(' ', '_')
            for candidate in target_candidates:
                if col_lower == candidate.lower().replace('-', '_'):
                    # appointment_outcome can have 3 values (No-Show, Attended, Cancelled)
                    if col == 'appointment_outcome':
                        return col
                    # Check if binary for other candidates
                    unique_vals = self.df[col].nunique()
                    if unique_vals == 2:
                        return col
        
        # Fallback: look for binary columns
        for col in self.df.columns:
            if self.df[col].nunique() == 2:
                logger.warning(f"Using binary column '{col}' as target (fallback)")
                return col
        
        raise ValueError("Could not detect target column. Please specify manually.")
    
    def preprocess_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Preprocess the dataset for modeling."""
        df = self.df.copy()
        
        # Encode target
        y = df[self.target_column].copy()
        
        # Special handling for appointment_outcome
        if self.target_column == 'appointment_outcome':
            y = y.apply(lambda x: 0 if str(x) == 'Attended' else 1)
            logger.info("Target mapped: Attended=0, No-Show/Cancelled=1")
        else:
            # Convert to binary (0/1)
            unique_vals = y.unique()
            if len(unique_vals) == 2:
                y = y.map({unique_vals[0]: 0, unique_vals[1]: 1})
        
        logger.info(f"Target distribution:\n{y.value_counts()}")
        if len(y.unique()) > 1:
            logger.info(f"No-show rate: {y.mean() * 100:.2f}%")
        
        # Drop target, ID-like columns, and leakage columns
        drop_columns = [self.target_column]
        # Reminder columns leak target information
        for leak_col in ['reminder_channel', 'reminder_sent']:
            if leak_col in df.columns and leak_col not in drop_columns:
                drop_columns.append(leak_col)
        for col in df.columns:
            col_lower = col.lower()
            if any(id_term in col_lower for id_term in ['id', 'uuid', 'code']):
                if col != self.target_column:
                    drop_columns.append(col)
        
        X = df.drop(columns=drop_columns, errors='ignore')
        
        # Identify column types
        categorical_cols = X.select_dtypes(include=['object', 'bool']).columns.tolist()
        numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        logger.info(f"Categorical columns ({len(categorical_cols)}): {categorical_cols}")
        logger.info(f"Numerical columns ({len(numerical_cols)}): {numerical_cols}")
        
        # Handle missing values
        for col in numerical_cols:
            X[col] = X[col].fillna(X[col].median())
        
        for col in categorical_cols:
            X[col] = X[col].fillna('Unknown')
        
        # Encode categorical variables
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le
        
        self.feature_columns = X.columns.tolist()
        logger.info(f"Features: {self.feature_columns}")
        
        return X, y
    
    def train_test_split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> None:
        """Split data into training and testing sets."""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y,
        )
        
        logger.info(f"Training set: {len(self.X_train)} samples")
        logger.info(f"Test set: {len(self.X_test)} samples")
        logger.info(f"Train no-show rate: {self.y_train.mean() * 100:.2f}%")
        logger.info(f"Test no-show rate: {self.y_test.mean() * 100:.2f}%")
    
    def scale_features(self) -> None:
        """Scale numerical features"""
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)
    
    def train_random_forest(self) -> Dict[str, Any]:
        """Train Random Forest classifier"""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
        )
        
        self.model.fit(self.X_train, self.y_train)
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.model, self.X_train, self.y_train, cv=cv, scoring='roc_auc')
        
        logger.info(f"Random Forest CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        
        return {
            "model": "RandomForest",
            "cv_auc_mean": float(cv_scores.mean()),
            "cv_auc_std": float(cv_scores.std()),
        }
    
    def evaluate(self) -> Dict[str, Any]:
        """Evaluate the trained model"""
        y_pred = self.model.predict(self.X_test)
        
        results = {
            "accuracy": accuracy_score(self.y_test, y_pred),
            "precision": precision_score(self.y_test, y_pred, zero_division=0),
            "recall": recall_score(self.y_test, y_pred, zero_division=0),
            "f1_score": f1_score(self.y_test, y_pred, zero_division=0),
            "confusion_matrix": confusion_matrix(self.y_test, y_pred).tolist(),
        }
        
        # ROC-AUC if possible
        try:
            y_prob = self.model.predict_proba(self.X_test)[:, 1]
            results["roc_auc"] = roc_auc_score(self.y_test, y_prob)
        except:
            results["roc_auc"] = None
        
        logger.info(f"Evaluation Results:")
        logger.info(f"  Accuracy: {results['accuracy']:.3f}")
        logger.info(f"  Precision: {results['precision']:.3f}")
        logger.info(f"  Recall: {results['recall']:.3f}")
        logger.info(f"  F1-Score: {results['f1_score']:.3f}")
        if results['roc_auc']:
            logger.info(f"  ROC-AUC: {results['roc_auc']:.3f}")
        
        return results
    
    def get_feature_importance(self) -> List[Dict[str, Any]]:
        """Get feature importance"""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importances = np.abs(self.model.coef_[0])
        else:
            return []
        
        feature_importance = sorted(
            zip(self.feature_columns, importances),
            key=lambda x: x[1],
            reverse=True,
        )
        
        logger.info("\nTop 10 Most Important Features:")
        for name, imp in feature_importance[:10]:
            logger.info(f"  {name}: {imp:.4f}")
        
        return [
            {"feature": name, "importance": float(imp)}
            for name, imp in feature_importance
        ]
    
    def save_model(self, path: str = "data/models/no_show_predictor") -> None:
        """Save trained model"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, f"{path}/model.pkl")
        joblib.dump(self.scaler, f"{path}/scaler.pkl")
        joblib.dump(self.label_encoders, f"{path}/label_encoders.pkl")
        
        with open(f"{path}/feature_columns.json", 'w') as f:
            json.dump(self.feature_columns, f)
        
        with open(f"{path}/target_column.txt", 'w') as f:
            f.write(self.target_column)
        
        logger.info(f"Model saved to {path}")


def main():
    """Main training function"""
    logger.info("=" * 60)
    logger.info("Starting No-Show Prediction Model Training")
    logger.info("=" * 60)
    
    predictor = NoShowPredictor()
    predictor.load_data()
    
    X, y = predictor.preprocess_data()
    predictor.train_test_split_data(X, y)
    predictor.scale_features()
    
    logger.info("\n--- Training Random Forest ---")
    predictor.train_random_forest()
    evaluation = predictor.evaluate()
    feature_importance = predictor.get_feature_importance()
    
    predictor.save_model()
    
    # Save results
    results = {
        "evaluation": evaluation,
        "feature_importance": feature_importance,
        "target_column": predictor.target_column,
    }
    
    results_path = Path("data/processed/no_show_model_results.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\nResults saved to {results_path}")
    logger.info("No-Show Prediction Model Training Complete!")
    
    return results


if __name__ == "__main__":
    main()

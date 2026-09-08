"""
HealthConnect AI - Model Evaluator
===================================
Comprehensive model evaluation utilities.

Features:
- Accuracy metrics
- Confusion matrix
- Precision/Recall/F1
- Cross-validation
- Error analysis
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, StratifiedKFold

from config.logging_config import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """
    Model evaluator for comprehensive evaluation.
    """
    
    def __init__(self):
        logger.info("ModelEvaluator initialized")
    
    def evaluate_classifier(
        self,
        y_true: List[int],
        y_pred: List[int],
        labels: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate classifier performance.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Label names
            
        Returns:
            Dict: Evaluation results
        """
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Classification report
        report = classification_report(
            y_true, y_pred, target_names=labels, output_dict=True, zero_division=0
        )
        
        results = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
            "total_samples": len(y_true),
        }
        
        return results
    
    def cross_validate(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        n_folds: int = 5,
    ) -> Dict[str, Any]:
        """
        Perform cross-validation.
        
        Args:
            model: Model to evaluate
            X: Features
            y: Labels
            n_folds: Number of folds
            
        Returns:
            Dict: Cross-validation results
        """
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        
        scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
        
        return {
            "mean_accuracy": float(np.mean(scores)),
            "std_accuracy": float(np.std(scores)),
            "fold_scores": scores.tolist(),
            "n_folds": n_folds,
        }
    
    def analyze_errors(
        self,
        y_true: List[int],
        y_pred: List[int],
        texts: List[str],
        labels: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Analyze misclassified examples.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            texts: Input texts
            labels: Label names
            
        Returns:
            List: Error analysis
        """
        errors = []
        
        for i, (true, pred, text) in enumerate(zip(y_true, y_pred, texts)):
            if true != pred:
                errors.append({
                    "index": i,
                    "text": text,
                    "true_label": labels[true] if true < len(labels) else str(true),
                    "predicted_label": labels[pred] if pred < len(labels) else str(pred),
                })
        
        return errors
    
    def evaluate_retrieval(
        self,
        retrieved_ids: List[List[str]],
        relevant_ids: List[List[str]],
        k_values: List[int] = [1, 3, 5, 10],
    ) -> Dict[str, Any]:
        """
        Evaluate retrieval performance.
        
        Args:
            retrieved_ids: Retrieved document IDs
            relevant_ids: Relevant document IDs
            k_values: K values for metrics
            
        Returns:
            Dict: Retrieval metrics
        """
        results = {}
        
        for k in k_values:
            precision_scores = []
            recall_scores = []
            mrr_scores = []
            
            for retrieved, relevant in zip(retrieved_ids, relevant_ids):
                retrieved_k = retrieved[:k]
                relevant_set = set(relevant)
                
                # Precision@K
                relevant_retrieved = set(retrieved_k) & relevant_set
                precision = len(relevant_retrieved) / k if k > 0 else 0
                precision_scores.append(precision)
                
                # Recall@K
                recall = len(relevant_retrieved) / len(relevant_set) if relevant_set else 0
                recall_scores.append(recall)
                
                # MRR
                for rank, doc_id in enumerate(retrieved_k, 1):
                    if doc_id in relevant_set:
                        mrr_scores.append(1 / rank)
                        break
                else:
                    mrr_scores.append(0)
            
            results[f"precision@{k}"] = float(np.mean(precision_scores))
            results[f"recall@{k}"] = float(np.mean(recall_scores))
            results[f"mrr@{k}"] = float(np.mean(mrr_scores))
        
        return results
    
    def generate_evaluation_report(
        self,
        model_name: str,
        metrics: Dict[str, Any],
    ) -> str:
        """
        Generate evaluation report.
        
        Args:
            model_name: Model name
            metrics: Evaluation metrics
            
        Returns:
            str: Report text
        """
        report = f"""
========================================
Model Evaluation Report: {model_name}
========================================

Overall Metrics:
- Accuracy: {metrics.get('accuracy', 'N/A'):.4f}
- Precision: {metrics.get('precision', 'N/A'):.4f}
- Recall: {metrics.get('recall', 'N/A'):.4f}
- F1 Score: {metrics.get('f1_score', 'N/A'):.4f}

Total Samples: {metrics.get('total_samples', 'N/A')}

========================================
"""
        return report
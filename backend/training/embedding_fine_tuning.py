"""
HealthConnect AI - Embedding Fine-Tuning
=========================================
Fine-tune embedding models for domain adaptation.

Features:
- Sentence-Transformer fine-tuning
- Domain-specific training
- Embedding evaluation
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from config.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingFineTuner:
    """
    Embedding fine-tuning for domain adaptation.
    """
    
    def __init__(self, model_dir: str = "data/models/embeddings"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        
        logger.info(f"EmbeddingFineTuner initialized with model_dir={model_dir}")
    
    def fine_tune(
        self,
        base_model: str = "all-MiniLM-L6-v2",
        train_pairs: Optional[List[Tuple[str, str, float]]] = None,
        epochs: int = 3,
        batch_size: int = 16,
    ) -> Dict[str, Any]:
        """
        Fine-tune embedding model.
        
        Args:
            base_model: Base model to fine-tune
            train_pairs: Training pairs (text1, text2, similarity_score)
            epochs: Number of epochs
            batch_size: Batch size
            
        Returns:
            Dict: Fine-tuning results
        """
        try:
            from sentence_transformers import SentenceTransformer, InputExample, losses
            from torch.utils.data import DataLoader
            
            logger.info(f"Fine-tuning {base_model}...")
            
            # Load base model
            self.model = SentenceTransformer(base_model)
            
            # Prepare training data
            if not train_pairs:
                train_pairs = self._generate_domain_pairs()
            
            train_examples = [
                InputExample(texts=[text1, text2], label=score)
                for text1, text2, score in train_pairs
            ]
            
            train_dataloader = DataLoader(
                train_examples,
                shuffle=True,
                batch_size=batch_size,
            )
            
            # Define loss
            train_loss = losses.CosineSimilarityLoss(self.model)
            
            # Fine-tune
            self.model.fit(
                train_objectives=[(train_dataloader, train_loss)],
                epochs=epochs,
                warmup_steps=100,
                show_progress_bar=True,
            )
            
            # Save model
            self.model.save(str(self.model_dir))
            
            logger.info(f"Saved fine-tuned model to {self.model_dir}")
            
            return {
                "status": "success",
                "base_model": base_model,
                "epochs": epochs,
                "train_examples": len(train_examples),
                "model_dir": str(self.model_dir),
            }
            
        except ImportError as e:
            logger.error(f"Fine-tuning failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
            }
    
    def _generate_domain_pairs(self) -> List[Tuple[str, str, float]]:
        """Generate domain-specific training pairs"""
        # HealthConnect domain pairs
        pairs = [
            ("appointment", "booking", 0.9),
            ("appointment", "schedule", 0.85),
            ("appointment", "visit", 0.8),
            ("cancel", "cancellation", 0.95),
            ("reschedule", "change appointment", 0.9),
            ("doctor", "physician", 0.85),
            ("clinic", "medical center", 0.8),
            ("billing", "payment", 0.85),
            ("insurance", "coverage", 0.8),
            ("prescription", "medication", 0.85),
            ("appointment", "surgery", 0.3),
            ("billing", "appointment", 0.2),
            ("doctor", "billing", 0.1),
            ("clinic", "prescription", 0.2),
            ("cancel", "book", 0.1),
        ]
        
        return pairs
    
    def evaluate(
        self,
        test_pairs: Optional[List[Tuple[str, str, float]]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate fine-tuned model.
        
        Args:
            test_pairs: Test pairs
            
        Returns:
            Dict: Evaluation results
        """
        if not self.model:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(str(self.model_dir))
        
        if not test_pairs:
            test_pairs = self._generate_domain_pairs()
        
        import numpy as np
        from scipy.stats import spearmanr
        
        predicted_scores = []
        true_scores = []
        
        for text1, text2, true_score in test_pairs:
            embedding1 = self.model.encode(text1)
            embedding2 = self.model.encode(text2)
            
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            predicted_scores.append(float(similarity))
            true_scores.append(true_score)
        
        correlation, p_value = spearmanr(predicted_scores, true_scores)
        
        return {
            "spearman_correlation": float(correlation),
            "p_value": float(p_value),
            "num_pairs": len(test_pairs),
        }
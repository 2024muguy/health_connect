"""
HealthConnect AI - Model Registry
==================================
Model versioning and registry management.

Features:
- Model versioning
- Model metadata tracking
- Model comparison
- Model deployment management
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """
    Model registry for versioning and deployment.
    """
    
    def __init__(self, registry_dir: str = "data/models"):
        self.registry_dir = Path(registry_dir)
        self.registry_file = self.registry_dir / "registry.json"
        self._registry = self._load_registry()
        
        logger.info(f"ModelRegistry initialized with registry_dir={registry_dir}")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from file"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        
        return {"models": {}}
    
    def _save_registry(self) -> None:
        """Save registry to file"""
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self._registry, f, indent=2)
    
    def register_model(
        self,
        model_name: str,
        version: str,
        model_type: str,
        metrics: Dict[str, Any],
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a model.
        
        Args:
            model_name: Model name
            version: Model version
            model_type: Model type (intent_classifier, safety_classifier, etc.)
            metrics: Model metrics
            file_path: Model file path
            metadata: Additional metadata
            
        Returns:
            Dict: Registration result
        """
        model_id = f"{model_name}_v{version}"
        
        entry = {
            "model_id": model_id,
            "model_name": model_name,
            "version": version,
            "model_type": model_type,
            "metrics": metrics,
            "file_path": file_path,
            "metadata": metadata or {},
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "registered",
        }
        
        self._registry["models"][model_id] = entry
        self._save_registry()
        
        logger.info(f"Registered model: {model_id}")
        return entry
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model by ID"""
        return self._registry["models"].get(model_id)
    
    def list_models(
        self,
        model_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List registered models"""
        models = list(self._registry["models"].values())
        
        if model_type:
            models = [m for m in models if m["model_type"] == model_type]
        
        return models
    
    def get_latest_version(
        self,
        model_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get latest version of a model"""
        models = [
            m for m in self._registry["models"].values()
            if m["model_name"] == model_name
        ]
        
        if not models:
            return None
        
        return max(models, key=lambda m: int(m["version"]))
    
    def compare_models(
        self,
        model_ids: List[str],
    ) -> Dict[str, Any]:
        """Compare multiple models"""
        comparison = {}
        
        for model_id in model_ids:
            model = self.get_model(model_id)
            if model:
                comparison[model_id] = {
                    "metrics": model["metrics"],
                    "registered_at": model["registered_at"],
                }
        
        return comparison
    
    def deactivate_model(self, model_id: str) -> None:
        """Deactivate a model"""
        if model_id in self._registry["models"]:
            self._registry["models"][model_id]["status"] = "inactive"
            self._save_registry()
            logger.info(f"Deactivated model: {model_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        models = self._registry["models"]
        
        return {
            "total_models": len(models),
            "model_types": list(set(m["model_type"] for m in models.values())),
            "active_models": sum(1 for m in models.values() if m["status"] == "registered"),
        }

## docs/Model_Training_Guide.md

```markdown
# HealthConnect AI - Model Training Guide

## Overview
Guide for training and evaluating ML models.

## Training Intent Classifier
```bash
python scripts/train_intent_classifier.py
Training Safety Classifier
bash
python scripts/train_safety_classifier.py
Using Jupyter Notebooks
Start notebook container:

bash
docker-compose up -d notebook
Access: http://localhost:8888

Navigate to notebooks/ directory

Notebook Workflow
01_exploratory_data_analysis.ipynb - Explore data

02_document_preprocessing.ipynb - Clean data

03_chunking_strategies.ipynb - Test chunking

08_intent_classifier_training.ipynb - Train intent model

09_safety_model_training.ipynb - Train safety model

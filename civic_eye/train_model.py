import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# Load dataset
df = pd.read_csv('data/dataset.csv')
print(f"Dataset size: {len(df)} rows")

# Train category model
X = df['text']
y_cat = df['category']
X_train, X_test, y_train_cat, y_test_cat = train_test_split(
    X, y_cat, test_size=0.2, random_state=42, stratify=y_cat
)

cat_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2))),
    ('clf', LogisticRegression(max_iter=1000, random_state=42)),
])

cat_pipeline.fit(X_train, y_train_cat)
y_pred_cat = cat_pipeline.predict(X_test)

cat_accuracy = accuracy_score(y_test_cat, y_pred_cat)
cat_report = classification_report(y_test_cat, y_pred_cat, output_dict=True, zero_division=0)
cat_cm = confusion_matrix(y_test_cat, y_pred_cat, labels=sorted(df['category'].unique()))

print(f"Category Model Accuracy: {cat_accuracy:.4f}")
print(f"Classification Report:\n{classification_report(y_test_cat, y_pred_cat)}")

# Train priority model
y_pri = df['priority']
X_train2, X_test2, y_train_pri, y_test_pri = train_test_split(
    X, y_pri, test_size=0.2, random_state=42, stratify=y_pri
)

pri_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2))),
    ('clf', LogisticRegression(max_iter=1000, random_state=42)),
])

pri_pipeline.fit(X_train2, y_train_pri)
y_pred_pri = pri_pipeline.predict(X_test2)

pri_accuracy = accuracy_score(y_test_pri, y_pred_pri)
pri_report = classification_report(y_test_pri, y_pred_pri, output_dict=True, zero_division=0)
pri_cm = confusion_matrix(y_test_pri, y_pred_pri, labels=sorted(df['priority'].unique()))

print(f"Priority Model Accuracy: {pri_accuracy:.4f}")
print(f"Classification Report:\n{classification_report(y_test_pri, y_pred_pri)}")

# Save models
os.makedirs('models', exist_ok=True)
joblib.dump(cat_pipeline, 'models/category_model.pkl')
joblib.dump(pri_pipeline, 'models/priority_model.pkl')
print("Models saved to models/ directory")

# Save confusion matrices as images
plt.figure(figsize=(8, 4))

plt.subplot(1, 2, 1)
plt.imshow(cat_cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('Category Confusion Matrix')
plt.colorbar()
tick_marks = np.arange(len(df['category'].unique()))
plt.xticks(tick_marks, df['category'].unique(), rotation=45)
plt.yticks(tick_marks, df['category'].unique())

for i in range(cat_cm.shape[0]):
    for j in range(cat_cm.shape[1]):
        plt.text(j, i, str(cat_cm[i, j]), ha="center", va="center", color="red")

plt.subplot(1, 2, 2)
plt.imshow(pri_cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('Priority Confusion Matrix')
plt.colorbar()
tick_marks2 = np.arange(len(df['priority'].unique()))
plt.xticks(tick_marks2, df['priority'].unique(), rotation=45)
plt.yticks(tick_marks2, df['priority'].unique())

for i in range(pri_cm.shape[0]):
    for j in range(pri_cm.shape[1]):
        plt.text(j, i, str(pri_cm[i, j]), ha="center", va="center", color="red")

plt.tight_layout()
plt.savefig('models/confusion_matrix.png')
print("Confusion matrix saved to models/confusion_matrix.png")

# Save metrics.json
metrics = {
    'dataset_size': len(df),
    'category_accuracy': float(cat_accuracy),
    'priority_accuracy': float(pri_accuracy),
    'category_classification_report': classification_report(y_test_cat, y_pred_cat, output_dict=True, zero_division=0),
    'priority_classification_report': classification_report(y_test_pri, y_pred_pri, output_dict=True, zero_division=0),
    'category_names': sorted(df['category'].unique()),
    'priority_names': sorted(df['priority'].unique()),
}

with open('models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("Metrics saved to models/metrics.json")

print("\nTraining complete!")
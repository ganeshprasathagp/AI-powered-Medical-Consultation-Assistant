# -*- coding: utf-8 -*-
"""Cardiac Health Advanced Monitoring System

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DkBY5iO4GnSkr2SBnvltMIehXcdtMm0y

***HEART ATTACK PREDICTION - ML MODEL ***
BY: Ganesh Prasath A

Data loading - dataset taken from kaggle
"""

import pandas as pd

file_path = 'heart.csv'
df = pd.read_csv(file_path)

df_info = df.info()
df_head = df.head()
df_describe = df.describe()

df_info, df_head, df_describe

"""***Data analysis***"""

missing_values_count = df.isnull().sum()
missing_values_count

"""Fitting the data"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


X = df.drop('output', axis=1)
y = df['output']

# Normalize the features using StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
#train test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
X_train.shape, X_test.shape, y_train.shape, y_test.shape

"""Models"""

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Initialize models
models = {
    'Logistic Regression': LogisticRegression(random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(),
    'Support Vector Machine': SVC(random_state=42),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42)
}


model_accuracies = {}

# Train and evaluate each model
for model_name, model in models.items():

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    model_accuracies[model_name] = accuracy

model_accuracies

"""The K-Nearest Neighbors seems to be the best model for this particular dataset. So we will be continuing with KNN.

Hyperparameter Tuning
"""

from sklearn.model_selection import GridSearchCV
import numpy as np

# Initialize KNN model
knn = KNeighborsClassifier()

param_grid = {
    'n_neighbors': np.arange(1, 21),  # Number of neighbors
    'weights': ['uniform', 'distance'],  # Weight function
    'metric': ['euclidean', 'manhattan', 'minkowski']  # Distance metric
}

grid_search = GridSearchCV(knn, param_grid, cv=5, scoring='accuracy')

grid_search.fit(X_train, y_train)

# Best accuracy
best_params = grid_search.best_params_
best_accuracy = grid_search.best_score_

best_params, best_accuracy

# Initialize KNN model with default parameters
knn_default = KNeighborsClassifier()
knn_default.fit(X_train, y_train)
y_pred_default = knn_default.predict(X_test)
default_accuracy = accuracy_score(y_test, y_pred_default)

# Initialize KNN model with best parameters
knn_best = KNeighborsClassifier(metric='manhattan', n_neighbors=8, weights='distance')
knn_best.fit(X_train, y_train)
y_pred_best = knn_best.predict(X_test)
best_accuracy_test = accuracy_score(y_test, y_pred_best)

default_accuracy, best_accuracy_test

"""Checking for overfitting and underfitting"""

#  accuracy of the default KNN model on the training set
y_pred_train_default = knn_default.predict(X_train)
train_accuracy_default = accuracy_score(y_train, y_pred_train_default)

#  accuracy of the optimized KNN model
y_pred_train_best = knn_best.predict(X_train)
train_accuracy_best = accuracy_score(y_train, y_pred_train_best)

#  comparison of accuracy
accuracy_comparison = {
    'Model': ['Default KNN', 'Optimized KNN'],
    'Train Accuracy': [train_accuracy_default, train_accuracy_best],
    'Test Accuracy': [default_accuracy, best_accuracy_test]
}

accuracy_comparison_df = pd.DataFrame(accuracy_comparison)
accuracy_comparison_df

"""Parameters"""

from sklearn.metrics import recall_score, f1_score, precision_score

#  Recall, F1 Score, and Precision for the default KNN model
recall = recall_score(y_test, y_pred_default)
f1 = f1_score(y_test, y_pred_default)
precision = precision_score(y_test, y_pred_default)

recall, f1, precision

"""Confusion matrix"""

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# Confusion Matrix for the default KNN model
plt.figure(figsize=(6, 6))
conf_matrix = confusion_matrix(y_test, y_pred_default)
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['No Heart Attack', 'Heart Attack'],
            yticklabels=['No Heart Attack', 'Heart Attack'])
plt.title('Confusion Matrix - Default KNN')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')

"""**Predicting heart attack risk for an user**"""

def explain_risk_factors(user_input):
    explanations = []

    low_risk_ranges = {
        'age': (30, 50),
        'trtbps': (90, 120),
        'chol': (150, 200),
        'fbs': (0, 0),
        'thalachh': (140, 190),
        'oldpeak': (0, 1),
        'caa': (0, 0)
    }

    for param, (low, high) in low_risk_ranges.items():
        value = user_input.get(param)

        if value is not None and (value < low or value > high):
            explanations.append(f"- {param.upper()} is not in the ideal range.")

    return explanations

#user input
def predict_heart_attack_risk():
    user_name, user_input = get_user_input()


    for key, value in user_input.items():
        if value is None:
            user_input[key] = df[key].median()


    user_df = pd.DataFrame([user_input], columns=X.columns)

    # Normalizing
    user_scaled = scaler.transform(user_df)

    # prediction
    prediction = knn_default.predict(user_scaled)
    prediction_prob = knn_default.predict_proba(user_scaled)

    # risk percentage
    risk_percentage = prediction_prob[0][1] * 100

    result = f"{user_name}, our model predicts that you have {'a high' if prediction[0] == 1 else 'a low'} risk of experiencing a heart attack. Your risk percentage is {risk_percentage:.2f}%."

    # Explain high-risk factors
    if prediction[0] == 1:
        result += "\n\nFactors contributing to high risk:"
        risk_factors = explain_risk_factors(user_input)

        if risk_factors:
            result += "\n" + "\n".join(risk_factors)
        else:
            result += "\n- No specific factors identified (consult a healthcare provider for a comprehensive evaluation)."

    return result

# Test the function by asking for user input and making a prediction
print(predict_heart_attack_risk())
1
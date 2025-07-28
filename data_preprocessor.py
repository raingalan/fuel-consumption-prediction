from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import pandas as pd
import numpy as np

class DataPreprocessor:
    """
    Takes the raw train / test data and one hot encodes categorical cols and standardizes numerical cols
    """

    def __init__(self, categorical_cols: list, numerical_cols: list):
        self.categorical_cols = categorical_cols
        self.numerical_cols = numerical_cols
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), self.categorical_cols),
                ('num', StandardScaler(), self.numerical_cols)
            ], remainder='passthrough')
        self.target_scaler = None
        self.all_cols = self.categorical_cols + self.numerical_cols

    def fit_transform(self, X: pd.DataFrame, y=None):
        # apply the preprocessor on the training data
        X_transformed = self.preprocessor.fit_transform(X)

        y_transformed = None
        if y is not None:
            if not isinstance(y, np.ndarray):
                y = y.to_numpy()
            self.target_scaler = StandardScaler()
            y_transformed = self.target_scaler.fit_transform(y.reshape(-1, 1)).ravel()

        return X_transformed, y_transformed

    def transform(self, X: pd.DataFrame, y=None):
        # apply the preprocessor on val and test data

        if isinstance(X, dict):
            X = pd.DataFrame(X)
        X_transformed = self.preprocessor.transform(X)

        if y is not None:
            if not isinstance(y, np.ndarray):
                y = y.to_numpy()
            y_transformed = self.target_scaler.transform(y.reshape(-1, 1)).ravel()
            return X_transformed, y_transformed

        return X_transformed

    def get_feature_preprocessor(self):
        if self.preprocessor is None:
            raise RuntimeError("Feature preprocessor is not fitted yet. Call fit_transform with data first.")
        return self.preprocessor

    def get_target_scaler(self):
        if self.target_scaler is None:
            raise RuntimeError("Target scaler is not fitted yet. Call fit_transform with data first.")
        return self.target_scaler
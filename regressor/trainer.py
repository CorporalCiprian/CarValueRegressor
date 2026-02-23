import pandas as pd
import numpy as np
import json
import re
import joblib
import requests

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error


def _get_curs_euro() -> float:
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR', timeout=5)
        return response.json()['rates']['RON']
    except Exception:
        return 4.97  # fallback


def _clean_price(x, curs_euro: float):
    if pd.isna(x):
        return np.nan
    x_str = str(x).lower().replace(' ', '').replace(',', '.')
    match = re.search(r'(\d+(\.\d+)?)', x_str)
    if not match:
        return np.nan
    pret = float(match.group(1))
    if 'lei' in x_str or 'ron' in x_str:
        pret = pret / curs_euro
    return pret


def _extract_number(x):
    if pd.isna(x):
        return np.nan
    val = re.sub(r'[^\d]', '', str(x))
    return float(val) if val else np.nan


FEATURES = ['Marca', 'Model', 'An', 'Rulaj', 'Putere', 'Combustibil', 'Cutie de viteze']
NUMERIC_FEATURES = ['An', 'Rulaj', 'Putere']
CATEGORICAL_FEATURES = ['Marca', 'Model', 'Combustibil', 'Cutie de viteze']


def train(json_path: str, model_path: str) -> dict:
    """
    Train the model from a JSON file and save it to model_path.
    Returns a dict with MAE and number of training samples.
    """

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    curs_euro = _get_curs_euro()

    flat_data = []
    for item in data:
        flat_item = {"price": item.get("price"), "source": item.get("source")}
        if "attributes" in item:
            flat_item.update(item["attributes"])
        flat_data.append(flat_item)

    df = pd.DataFrame(flat_data)

    df['price'] = df['price'].apply(lambda x: _clean_price(x, curs_euro))
    df['An'] = df['Anul producției'].combine_first(df['An de fabricatie'])
    df['Usi'] = df['Numar de portiere'].combine_first(df['Numar de usi'])
    df['An'] = df['An'].apply(_extract_number)
    df['Rulaj'] = df['Rulaj'].apply(_extract_number)
    df['Putere'] = df['Putere'].apply(_extract_number)

    df_clean = df[FEATURES + ['price']].dropna(subset=['price'])
    df_clean = df_clean[(df_clean['price'] >= 1000) & (df_clean['price'] <= 200000)]

    X = df_clean[FEATURES]
    y = df_clean['price']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, NUMERIC_FEATURES),
        ('cat', categorical_transformer, CATEGORICAL_FEATURES)
    ])

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=0))
    ])

    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))
    joblib.dump(model, model_path)

    return {
        'mae': round(mae, 2),
        'samples': len(df_clean),
        'model_path': model_path
    }


def predict(model_path: str, car: dict) -> float:
    """
    Predict the price of a car given a dict with its attributes.

    Example car dict:
    {
        "Marca": "Volkswagen",
        "Model": "Golf",
        "An": 2018,
        "Rulaj": 85000,
        "Putere": 115,
        "Combustibil": "Benzina",
        "Cutie de viteze": "Manuala"
    }

    Returns the predicted price in EUR.
    """
    model = joblib.load(model_path)
    df = pd.DataFrame([car])
    return float(model.predict(df)[0])
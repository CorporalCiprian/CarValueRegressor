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

with open('car_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

flat_data = []
for item in data:
    flat_item = {"price": item.get("price"), "source": item.get("source")}
    if "attributes" in item:
        flat_item.update(item["attributes"])
    flat_data.append(flat_item)

df = pd.DataFrame(flat_data)


def clean_price(x):
    if pd.isna(x): return np.nan
    x_str = str(x).lower().replace(' ', '').replace(',', '.')
    match = re.search(r'(\d+(\.\d+)?)', x_str)
    if not match:
        return np.nan
    pret = float(match.group(1))
    if 'lei' in x_str or 'ron' in x_str:
        pret = pret / CURS_EURO
    return pret


def extract_number(x):
    if pd.isna(x): return np.nan
    val = re.sub(r'[^\d]', '', str(x))
    return float(val) if val else np.nan


def get_curs_euro():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR')
        data = response.json()
        curs = data['rates']['RON']
        print(f"Exchange rate: 1 EUR = {curs} RON")
        return curs
    except Exception as e:
        print("Using fallback rate(API or internet failure)")
        return 4.97
CURS_EURO = get_curs_euro()


df['price'] = df['price'].apply(clean_price)

df['An'] = df['Anul producției'].combine_first(df['An de fabricatie'])
df['Usi'] = df['Numar de portiere'].combine_first(df['Numar de usi'])

df['An'] = df['An'].apply(extract_number)
df['Rulaj'] = df['Rulaj'].apply(extract_number)
df['Putere'] = df['Putere'].apply(extract_number)

features = ['Marca', 'Model', 'An', 'Rulaj', 'Putere', 'Combustibil', 'Cutie de viteze']
target = 'price'

df_clean = df[features + [target]].dropna(subset=[target])

df_clean = df_clean[(df_clean['price'] >= 1000) & (df_clean['price'] <= 200000)]

X = df_clean[features]
y = df_clean[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

numeric_features = ['An', 'Rulaj', 'Putere']
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_features = ['Marca', 'Model', 'Combustibil', 'Cutie de viteze']
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=0))
])

print("Training model...")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean absolute error on test dataset: {mae:.2f} EUR")

joblib.dump(model, 'CarValueRegressor.pkl')
print("Model saved successfully as 'CarValueRegressor.pkl'!")
# Carbon Footprint Analysis Summary


## Overview
This analysis predicts total CO₂e emissions using the `Carbon_Footprint_Data.csv` dataset. It includes data preprocessing, exploratory data analysis (EDA), and modeling with Random Forest, XGBoost, LSTM, and GRU.

## Key Components

### 1. Data Loading and Preprocessing
- **Dataset**: `Carbon_Footprint_Data.csv` with 15,000 rows and 30 columns.
- **Cleaning**:
  - Fixed column name encoding (e.g., `â‚₂` to `2`).
  - Converted `Timestamp_Date` to datetime, extracted `Year`, `Month`, `Day`.
  - Mapped `Temperature_Control` to binary (1/0).
  - Dropped columns: `Timestamp_Date`, `Transaction_ID`, `Product_ID`, `Supplier_ID`.
- **Outlier Handling**: Winsorization (5th/95th percentiles) on numeric features.
- **Preprocessing Pipeline**:
  - Numeric features: Winsorized, scaled (`StandardScaler`).
  - Categorical features: One-hot encoded (`OneHotEncoder`).
  - Saved as `preprocessor.pkl`.

### 2. Exploratory Data Analysis (EDA)
- **Visualizations**:
  - Histogram with KDE for `CO₂e_Total`.
  - Correlation heatmap for 18 numeric features.
  - Boxplots for numeric columns.
  - Q-Q and distribution plots for normality.
- **Skewness**: [-0.03, 0.03] across numeric columns.
- **Findings**: No missing values, near-normal distributions.

### 3. Data Splitting
- **Split**:
  - Training: 70% (10,500 samples)
  - Validation: 15% (2,250 samples)
  - Test: 15% (2,250 samples)
- **LSTM/GRU**: Data reshaped to `(samples, 1, features)` with single time step.

### 4. Model Training and Evaluation
#### Random Forest Regressor
- **Configuration**: Default parameters, random_state=42, saved as random_forest_model.pkl
- **Performance** (Test Set):
  - RMSE: 36.2596
  - MAPE: 0.0155
  - R²: 0.9508

#### XGBoost Regressor
- **Configuration**: Objective reg:squarederror, random_state=42
- **Performance** (Test Set):
  - RMSE: 28.3152
  - MAPE: 0.0123
  - R²: 0.9700

#### LSTM Model
- **Configuration**: 64 units, ReLU, Dropout 20%, Dense 32, Adam optimizer, MSE loss, 50 epochs, batch size 32, saved as lstm_model.h5
- **Performance** (Test Set):
  - RMSE: 25.9849
  - MAPE: 0.0107
  - R²: 0.9743

#### GRU Model
- **Configuration**: 64 units, ReLU, Dropout 20%, Dense 32, Adam optimizer, MSE loss, 50 epochs, batch size 32, saved as gru_model.h5
- **Performance** (Test Set):
  - RMSE: 25.4322
  - MAPE: 0.0106
  - R²: 0.9754

### 5. Evaluation Metrics
- **Metrics**: RMSE (error magnitude), MAPE (percentage error), R² (variance explained).
- **Comparison**:
  - GRU performed best (RMSE: 25.4322, R²: 0.9754).
  - LSTM closely followed (RMSE: 25.9849, R²: 0.9743).
  - XGBoost outperformed Random Forest.

### 6. Visualizations
- Learning curves (Random Forest, XGBoost).
- Loss curves (LSTM, GRU).
- Actual vs. Predicted plots for all models.

## Dependencies
- pandas, numpy, matplotlib, seaborn, scikit-learn, xgboost, tensorflow, feature_engine, scipy, joblib

## Output Files
- **Models**: `random_forest_model.pkl`, `lstm_model.h5`, `gru_model.h5`
- **Preprocessor**: `preprocessor.pkl`

## Key Insights
- **Data**: Clean, no missing values, minimal skewness.
- **Performance**: GRU and LSTM outperformed tree-based models; GRU is the best.
- **Features**: Likely driven by `Energy_Consumed_kWh`, `Distance_km`, `Load_Weight_kg`.


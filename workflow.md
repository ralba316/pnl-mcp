# Anomaly Detection Workflows

## 1. Input Delta Anomaly Detection (Primary Method)

**Most effective approach for finding data input anomalies:**

```python
# Load the Data sheet (not Pivot sheet)
df = pd.read_excel('PNL Explained Pivot v3.xlsx', sheet_name='Data')

# Calculate input deltas
df['Inp_Delta'] = df['Inp Today'] - df['Inp Yesterday']
df['Abs_Inp_Delta'] = df['Inp_Delta'].abs()

# Filter for valid data
valid_mask = df['Inp Today'].notna() & df['Inp Yesterday'].notna()
valid_mask &= (df['Inp Today'] != 0) | (df['Inp Yesterday'] != 0)
valid_inp = df[valid_mask]

# Find the largest input delta anomaly
anomaly_idx = valid_inp['Abs_Inp_Delta'].idxmax()
anomaly_row = df.loc[anomaly_idx]

# Display top 10 anomalies
top_anomalies = valid_inp.nlargest(10, 'Abs_Inp_Delta')
print(top_anomalies[['Deal Num', 'Ins Type', 'Inp Yesterday', 'Inp Today', 'Inp_Delta', 'Abs_Inp_Delta', 'Base PNL']])
```

**Confirmed Anomaly Found:**
- **Row 2, Deal 1015114**: Input delta of 2.08 (from -0.88 to 1.20)
- **Percentage Change**: -237.14%
- **Instrument**: COMM-PHYS (Physical Commodity)
- **Portfolio**: Canada
- **Impact**: Base Impact of Delta = 457,265

## 2. Statistical Overview (Supporting Analysis)

Use `.describe()` to get statistical radar for outliers:

```python
df[['Base PNL', 'Base Impact of Delta', 'Base Impact of Fx', 'Base Impact of Spot']].describe()
```

**What to look for:**
- Max values significantly higher than 75th percentile
- Min values significantly lower than 25th percentile  
- Large standard deviation relative to mean
- Extreme outliers beyond typical ranges

**Validation of Deal 1015114:**
- Base Impact of Delta: 457,264.54 (massive outlier)
- Input change from negative (-0.88) to positive (1.20)
- Z-score > 2.0 (statistically exceptional)

## 3. Automated Testing Framework

**Run comprehensive anomaly detection tests:**

```bash
# Run the anomaly detection test suite
pytest tests/test_anomaly.py -v

# Run all analysis tests including anomaly detection
pytest tests/test_analysis.py tests/test_anomaly.py -v
```

**Test Coverage:**
- `TestAnomalyDetection`: Core anomaly detection validation
- `TestAnomalyContext`: Context analysis (portfolio, buy/sell patterns)
- `TestAnomalyValidation`: Statistical validation (z-score, uniqueness)
- Validates Deal 1015114 as the primary input delta anomaly

## 4. Price Input Validation

Look for impossible price movements in commodity data:

```python
# Find extreme price changes
df[df['Base Impact of Delta'] > 400000][['Deal Num', 'Data Type', 'Base PNL', 'Base Impact of Delta', 'Index', 'Yesterday Delta', 'Inp Today', 'Inp Yesterday']]
```

**Red flags:**
- Negative commodity prices (`Inp Yesterday: -0.875`)
- Massive price swings (from -0.875 to 1.2)
- Delta impacts over 400,000
- Price movements that violate market fundamentals

## 5. Delta Impact Analysis

Identify deals with extreme delta sensitivity:

```python
# Find negative delta impacts below threshold
df[df['Base Impact of Delta'] < -50000][['Deal Num', 'Data Type', 'Base PNL', 'Base Impact of Delta', 'Index', 'Start Date', 'End Date']]
```

**Patterns to investigate:**
- Same deal number with multiple extreme impacts
- Consistent negative impacts across time periods
- Delta impacts without corresponding PNL changes

## 6. Deal-Level Anomaly Detection

Focus on specific deals showing unusual behavior:

```python
# Examine specific deal details
deal_1015114 = df[df['Deal Num'] == 1015114]
deal_1015114[['Data Type', 'Base Impact of Delta', 'Yesterday Delta', 'Inp Today', 'Inp Yesterday', 'Index']]
```

**Key indicators:**
- Yesterday Delta: 220,367.45
- Input price change from negative to positive
- Natural gas index (NG_BS_AB_NIT_ICE)
- Single deal causing major portfolio impact

## 7. Index-Specific Analysis

Analyze by commodity index for sector-specific anomalies:

```python
# Group by index to find problematic commodities
df.groupby('Index')['Base Impact of Delta'].agg(['count', 'mean', 'std', 'min', 'max'])
```

**Focus areas:**
- Natural gas indices (NG_BS_AB_NIT_ICE)
- Deals with high volatility
- Indices showing unusual concentration of impacts
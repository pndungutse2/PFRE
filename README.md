# ML-Powered Personalized Financial Recommendation Engine 
This is a machine learning-driven personal finance recommendation system that analyses user's spending behaviors
financial health, and risk signals to generate explainable, personalized financial actions aligned with US personal finance best practices 

The goal is to help users make better day-to-day financial decisions, including what to save, where to cut back, and when to invest. 

#key Features
1. Spending Behavior Analysis: Understands user expense patterns across categories and time
2. User Segmentation: Cluster users into financial personas using unsupervised learning
3. Financial Health Score: Compute composite score based on savings rate, expense stability, debt ratio, and emergency funds coverage
4. Personalized Recommendation: Generate actionable, user-specific financial guidance (save more, reduce spending, invest, or maintain what you have)

# Machine Learning Approach 
1. Features
2. User Segmentation
3. Financial Health Score
4. Recommendation Engine

# Evaluation Metrics

# Tech Stack
1. Language: Python
2. 

## Author 
### Patrick Ndungutse
### Machine Learning | FinTech | Data Science


# Dataset Description

## Personal Checking Transactions Dataset (v1.0)

### Dataset Objective

This dataset was constructed to support multiple applied machine learning tasks on financial transaction data, including:

-Transaction classification (e.g., spending category prediction)

-Cash-flow forecasting (short-term balance and expenditure trends)

-Anomaly detection (unusual or potentially erroneous transactions)

The primary goal is to demonstrate end-to-end data engineering, feature construction, and ML-readiness using real-world financial data.

## Data Source

The dataset was derived from monthly checking account statements issued by a major U.S. financial institution (Chase Bank) in PDF format. Statements were generated directly by the bank and represent finalized (posted) transactions.

All data extraction and processing were performed programmatically using Python-based PDF parsing utilities.

## Time Coverage

The dataset spans January 2023 through December 2024, covering multiple calendar years to capture seasonal spending patterns.

## Unit of Observation

Each record represents a single posted checking account transaction, including both debits and credits.

### Dataset Size

Number of transactions: ~4,000–5,000 (varies by version)

Number of statement files: 4 years  monthly PDFs

Number of features: 7–10, depending on feature engineering stage

### Feature Description
-Feature Name	Type	Description
-date	datetime	Transaction posting date
-description	string	Merchant and transaction details (free-text)
-amount	float	Signed transaction amount (negative = debit, positive = credit)
-balance	float	Account balance after the transaction
-category	string	Transaction category label (rule-based)
-month	period	Transaction month (YYYY-MM)
-weekday	string	Day of week
-source_file	string	Originating statement PDF
-transaction_id	string	Derived hash used for deduplication

## Data Collection and Processing Pipeline

Raw PDF statements were batch-ingested from a local directory. Transactions were extracted using line-based text parsing, where transaction boundaries were identified via date pattern recognition. Multi-line transaction descriptions were reconstructed using stateful parsing logic.

Monetary values were normalized to floating-point format, and transactions appearing in overlapping statement periods were deduplicated using a composite key of date, description, and amount. All transformations were performed in Python using reproducible scripts.

### Data Cleaning and Filtering

-Non-transaction rows (e.g., “Beginning Balance”) were removed

-Records with missing or malformed monetary values were dropped (<1%)

-No statistical imputation was performed

-All amounts are expressed in U.S. dollars

### Labeling Strategy

Transaction categories were assigned using a deterministic keyword-based matching approach applied to transaction descriptions. Labels were not manually validated and should be considered weakly supervised, suitable for baseline classification models and feature engineering demonstrations.

## Intended ML Tasks
### Classification

-Predict transaction category from description and amount

-Benchmark traditional ML vs. embedding-based models

### Forecasting

-Monthly expenditure forecasting

-Short-term balance trend prediction

### Anomaly Detection

-Detection of unusually large or infrequent transactions

-Identification of deviations from historical spending patterns

## Known Limitations

-Merchant names are not standardized and may appear under multiple aliases

-Category labels are heuristic and may contain noise

-Cash withdrawals cannot be attributed to specific merchants

-Dataset represents a single individual and is not population-representative

## Ethical and Privacy Considerations

The dataset contains sensitive financial information and is intended solely for personal analytical and portfolio demonstration purposes. No third-party data is included, and all processing complies with data ownership and privacy expectations.

## Versioning and Maintenance

Version 1.0 represents the initial cleaned and normalized release. Future versions may include improved merchant normalization, enhanced labeling, and additional engineered features.

### Portfolio Note 

This project emphasizes data quality, reproducibility, and transparency over model complexity, reflecting real-world constraints in applied machine learning workflows.
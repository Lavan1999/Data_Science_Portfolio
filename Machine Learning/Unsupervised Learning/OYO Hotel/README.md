# OYO Hotel Rooms Dataset Analysis Workflow
## Data Preprocessing

- Loading the Dataset: Loaded the OYO Hotel Rooms dataset from the provided CSV file using Pandas.
- Handling Missing Values: Removed rows with any missing values using dropna() function.
- Cleaning the Discount Column: Removed the '% off' suffix from the 'Discount' column values using a lambda function.
- Dropping Unnecessary Columns: Removed the 'Hotel_name' and 'Unnamed: 0' columns as they were not relevant to the analysis.
- Dropping Duplicates: Removed duplicate rows from the dataset using drop_duplicates() function.
## Natural Language Processing (NLP)
- Text Vectorization: Utilized CountVectorizer from Scikit-learn to convert location text data into a matrix of token counts.
## Machine Learning - Clustering
- Concatenating Features: Combined the location vectorized data with 'Price', 'Rating', and 'Discount' columns to create the feature matrix for clustering.
- KMeans Clustering: Employed the KMeans algorithm to cluster the data into different groups.
- Determining Optimal Number of Clusters: Used the Elbow Method to find the optimal number of clusters by plotting the within-cluster sum of squares (WCSS) against the number of clusters.
- Training KMeans Model: Trained the KMeans model with the optimal number of clusters determined from the Elbow Method.
- Assigning Clusters: Assigned each data point to its corresponding cluster using the fit_predict() function.
## Result Analysis
- Cluster Distribution: Analyzed the distribution of data points across different clusters using value_counts().

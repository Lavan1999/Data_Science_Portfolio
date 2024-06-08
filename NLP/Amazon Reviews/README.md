# AmazonReview

# Data Loading and Exploration:
- Load the dataset using pandas.
- Check the first few rows and general information of the dataframe.
- Verify if there are any missing values in the review column.
# Sentiment Analysis:
- Download the VADER lexicon from NLTK.
- Initialize the SentimentIntensityAnalyzer.
- Apply sentiment analysis to each review using VADER.
- Calculate the compound sentiment score for each review.
- Classify reviews as positive or negative based on the compound score.
- Calculate the accuracy score of the sentiment analysis.
 3 NLP - Natural Language Processing:
- Load the English language model from spaCy.
- Process each review to extract vector representations using spaCy.
# Machine Learning:
- Prepare the data for machine learning by using the vector representations of the reviews as features and the label column as the target variable.
- Split the data into training and testing sets.
- Train a Support Vector Machine (SVM) model on the training data.
- Make predictions on the test data using the trained model.
# Evaluation:
- Evaluate the performance of the SVM model.
- Calculate the accuracy score of the model.
- Generate a classification report to examine precision, recall, and F1-score for each class [positive and negative].

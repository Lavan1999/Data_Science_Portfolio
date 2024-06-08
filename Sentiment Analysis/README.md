# SmsSpamCollections

## Data Loading and Exploration:
- Loaded the dataset from Google Drive using pandas.
- Explored the dataset's structure and information.
- Checked for missing values in the dataset.
  
## Sentiment Analysis:
- Used NLTK's VADER sentiment analyzer to analyze the sentiment of text messages.
- Calculated a compound sentiment score for each message.
- Classified messages as "ham" or "spam" based on the compound score.
  
## NLP - Natural Language Processing:
- Utilized spaCy to process text messages and generate vector representations.
  
## Machine Learning:
- Concatenated spaCy-generated message vectors with 'length' and 'punct' features.
- Split the dataset into training and testing sets.
- Trained a Support Vector Machine (SVM) model on the training data.
- Made predictions on the test data using the trained model.
  
## Evaluation:
- Evaluated the SVM model'


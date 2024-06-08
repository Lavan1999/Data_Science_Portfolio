# Dataset-25_Real-FakeNewsDataset_NLP
# NLP- Process
1. Tokenization:
Tokenization involves breaking down a sentence or text into smaller units, such as words or phrases.
In the provided code, we use the word_tokenize() function from the NLTK library to tokenize each title in the 'title' column.
This step is essential because it prepares the text for further analysis by converting it into a format that can be processed more easily.
2. Lowercasing:
Converting all tokens to lowercase helps ensure consistency in your text data.
It prevents the model from treating words like "Hello" and "hello" differently, which could lead to inconsistencies in analysis or modeling.
3. Removing Stopwords:
Stopwords are common words like 'the', 'is', 'and', etc., which don't usually add much meaning to the text.
Removing stopwords helps reduce noise in your data and focuses on the more meaningful words.
We use NLTK's stopwords corpus to obtain a list of English stopwords and then remove them from the tokenized text.
4. Stemming or Lemmatization:
Stemming and Lemmatization are techniques used to reduce words to their root form.
In the provided code, we use the Porter Stemmer from NLTK to perform stemming.
Stemming helps to normalize words by reducing them to their base or root form, which can reduce the number of unique tokens in the dataset.
However, stemming can sometimes produce words that are not actual words, whereas lemmatization aims to return the base or dictionary form of a word.
5. Named Entity Recognition (NER):
Named Entity Recognition (NER) is a process of identifying named entities (such as names of people, organizations, locations, etc.) in text.
We use the spaCy library, which provides a pre-trained model for NER.
The NER model identifies entities in the text and assigns them labels such as PERSON, ORG, LOC, etc.
This step can be useful for extracting important information from the text, such as the names of people or organizations mentioned in news of headlines.

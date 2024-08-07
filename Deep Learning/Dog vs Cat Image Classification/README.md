# Dog vs Cat image classification

## Configure Kaggle API:
- Objective: Enable access to Kaggle datasets.
- Steps: Create a .kaggle directory in your system's home directory. Place the kaggle.json file, which contains your Kaggle API credentials, in this directory. Set the appropriate permissions to ensure security.

## Download and Extract Dataset:
- Objective: Obtain and prepare the dataset for analysis.
- Steps: Use the Kaggle API to download the dataset. The dataset typically comes in a zip file format. Extract these zip files to access the contained data files.

## Resize Images and Create Labels:
- Objective: Standardize image sizes and organize data for training.
- Steps: Resize all images to 224x224 pixels to ensure consistency. Assign labels to each image based on the filename, typically using prefixes like 'dog' or 'cat'. Store these labeled images in a separate directory.

## Load Data and Split:
- Objective: Prepare the dataset for model training and evaluation.
- Steps: Load the resized images and their corresponding labels into numpy arrays. Split the dataset into training and testing sets to facilitate model training and performance evaluation.

## Build and Train Model:
- Objective: Create a neural network to classify images.
- Steps: Use TensorFlow to build a neural network model. Employ a pre-trained MobileNet model as a feature extractor to leverage transfer learning. Train the model on the training set while monitoring its performance.

##Evaluate and Predict:
- Objective: Assess model performance and make predictions.
- Steps: Evaluate the trained model on the test set to determine its accuracy. Use the model to predict the class of new images by processing them through the model and interpreting the output.

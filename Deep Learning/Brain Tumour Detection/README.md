# BrainTumourDetection

colab : https://colab.research.google.com/drive/1XocwmAE5I2O3-sNK-pnFqsszqPGAWlZO?usp=sharing

![image](https://github.com/user-attachments/assets/892dd97d-9b0a-402f-9b61-063a6dca8a6c)


- Brain Tumor Detection Project Workflow
## 1. Project Overview
- Objective: Detect brain tumors using deep learning models with the highest possible accuracy due to the critical nature of medical diagnostics.
- Dataset: Medical images categorized as Positive (with tumor) and Negative (without tumor).
## 2. Data Preparation
- Dataset Structure:
The data is divided into three sets: Training (70%), Validation (15%), and Testing (15%).
Images are organized in separate folders based on their labels.
- Data Augmentation:
Applied techniques like zoom, shear, and horizontal flipping to enhance the model's ability to generalize.
## 3. Initial Model Development
- Model Architecture:
A Convolutional Neural Network (CNN) was constructed with multiple layers, including convolutional, max-pooling, dropout, and dense layers.
- Model Training:
The model was trained using the training set, with validation performed using the validation set.
- Initial Results:
The model achieved a 93% accuracy on the test data.
- Issue:
Although 93% is generally high, the 7% error margin is not acceptable for medical diagnostics, where precision is paramount.
## 4. Model Improvement
- Switch to Transfer Learning:
Recognizing the limitations of the initial model, a MobileNet-based model was adopted. MobileNet is a pre-trained model known for its efficiency in handling image classification tasks.
- Model Architecture Adjustments:
The MobileNet layers were used as the base, with additional layers added for classification. The base layers were frozen to retain learned features, and new dense layers were trained on the brain tumor dataset.
## 5. Training and Optimization
- Training Strategy:

The model was retrained using the same dataset splits, with callbacks for early stopping and model checkpointing to avoid overfitting and save the best-performing model.
- Evaluation:

The improved model was evaluated on the test set to assess its performance.
## 6. Results
- Final Accuracy:
The enhanced model achieved significantly better accuracy, reducing the error margin to meet medical standards.
## 7. Conclusion
- Outcome:
The project successfully developed a brain tumor detection model with a high level of accuracy suitable for medical applications.
- Next Steps:
Further refinement could involve testing other architectures, increasing dataset size, or applying more advanced augmentation techniques to push accuracy even higher.

# VIVA: TF-IDF, Logistic Regression, and Model Evaluation
## SIH25031 - Crowdsourced Civic Issue Reporting System

---

## What is TF-IDF?
**TF-IDF** stands for **Term Frequency - Inverse Document Frequency**. It's a mathematical formula that converts text into numbers that machines can understand and compare.

### Why do we need it?
Computers don't understand English or Hindi like humans do. They only understand numbers. TF-IDF helps us:
- Convert raw text (complaint sentences) into numerical vectors
- Give more importance to important words and less to common words
- Allow machines to compare different complaints mathematically

### How does it work? (Beginner explanation)

#### 1. **Term Frequency (TF)**
- Counts how many times a word appears in a document
- Example: In the sentence "road has pothole", "road" appears 1 time, "has" appears 1 time, "pothole" appears 1 time
- Simple count of word occurrences

#### 2. **Inverse Document Frequency (IDF)**
- Measures how rare or common a word is across ALL documents
- Common words like "the", "is", "are" appear in every document
- Rare words are more informative about the document's topic
- Formula: `log(total_documents / documents_containing_word)`

#### 3. **TF-IDF = TF × IDF**
- Words that appear frequently in **one** document but rarely in **other** documents get high scores
- This helps the model understand: "This word is important for this specific complaint!"

### Example
Imagine these two complaints:
- Document 1: "road has pothole"
- Document 2: "road is damaged"

Word "road" appears in both documents → IDF is low → TF-IDF is low
Word "pothole" appears only in Document 1 → IDF is high → TF-IDF is high
Word "damaged" appears only in Document 2 → IDF is high → TF-IDF is high

The model learns that "pothole" suggests category = Pothole, while "damaged" might suggest something else.

---

## What is Logistic Regression?
**Logistic Regression** is a classification algorithm - it predicts which CATEGORY or PRIORITY a complaint belongs to.

### Beginner analogy:
Imagine you have a basket of fruits. You want to teach a computer to distinguish between:
- Apples
- Oranges
- Bananas

You look at features like:
- Color (red, orange, yellow)
- Size (small, medium, large)
- Shape (round, curved, straight)

Logistic Regression finds the best boundaries between these categories based on the features it sees. In our case, the "features" are the important words identified by TF-IDF.

### How it works in our system:
1. **Input:** A complaint text (title + description)
2. **TF-IDF converts** the text into numerical features
3. **Logistic Regression** predicts: "This is likely a Pothole issue" with 85% confidence
4. **Output:** Category name + confidence percentage

---

## Train-Test Split (80/20)
We split our dataset into two parts:

- **Training set (80%):** Used to TEACH the model
- **Test set (20%):** Used to EVALUATE how well the model learned

### Why do we split?
If we train and test on the same data, the model will just memorize the answers (overfitting). It won't work on new, unseen complaints.

### The 80/20 split ensures:
- The model learns on most of the data (80%)
- We get an honest evaluation on remaining data (20%)
- The evaluation is realistic - the model must predict complaints it hasn't seen before

### Stratified Split
Our split is **stratified**, meaning:
- Both training and test sets have the SAME proportion of categories
- If 20% of all complaints are "High priority", then ~20% of both sets will be High priority
- This ensures fair evaluation even with imbalanced classes

---

## Model Evaluation Metrics

### 1. **Accuracy**
- **What it measures:** Percentage of predictions that are correct
- **Formula:** `Correct predictions / Total predictions`
- **Example:** 85% accuracy means 85 out of 100 complaints were predicted correctly
- **In our system:** Printed for both category and priority models

### 2. **Precision**
- **What it measures:** Of all complaints predicted as "X category", how many actually ARE "X category"
- **Formula:** `True Positives / (True Positives + False Positives)`
- **Example:** If model predicts 10 complaints as "Pothole", and 8 are actually potholes → Precision = 80%
- **Why it matters:** High precision means few false alarms

### 3. **Recall**
- **What it measures:** Of all actual "X category" complaints, how many did the model correctly predict
- **Formula:** `True Positives / (True Positives + False Negatives)`
- **Example:** If there are 15 actual pothole complaints, and model finds 12 → Recall = 80%
- **Why it matters:** High recall means we catch most real issues

### 4. **F1 Score**
- **What it measures:** Harmonic mean of Precision and Recall
- **Why it matters:** Balances precision and recall. A model can have high precision but low recall (or vice versa). F1 gives the overall quality.
- **Formula:** `2 × (Precision × Recall) / (Precision + Recall)`

---

## Confusion Matrix
A **Confusion Matrix** is a table that shows exactly what the model got right and wrong.

### Beginner explanation:
Imagine a matrix where:
- **Rows** = Actual categories (what the complaint really is)
- **Columns** = Predicted categories (what the model thinks it is)

### Example for our 6 categories:

| \ Actual/Predicted | Pothole | Garbage | Streetlight | Water Leakage | Drainage | Other |
|---|---|---|---|---|---|---|
| **Pothole** | 40 | 5 | 2 | 1 | 3 | 3 |
| **Garbage** | 3 | 35 | 2 | 1 | 2 | 4 |
| **Streetlight** | 2 | 1 | 30 | 3 | 1 | 2 |
| **Water Leakage** | 1 | 0 | 2 | 28 | 3 | 1 |
| **Drainage** | 2 | 1 | 1 | 2 | 25 | 3 |
| **Other** | 3 | 2 | 1 | 1 | 2 | 23 |

### Reading the matrix:
- **Diagonal (top-left to bottom-right):** Correct predictions
  - 40 potholes correctly identified as potholes
  - 35 garbage correctly identified as garbage
  - etc.
- **Off-diagonal:** Wrong predictions (confusions)
  - 5 potholes mistaken for garbage
  - 3 potholes mistaken for drainage
  - etc.

### Why it matters:
- Shows which categories the model confuses most
- Helps identify if the model is bad at one specific category
- In our admin dashboard, we show these matrices so admins can see model performance

---

## 10 Likely Teacher Questions & Answers

### Q1: What is TF-IDF and why did you use it?
**A:** TF-IDF converts text into numerical vectors by measuring how important words are in a document relative to a collection of documents. We used it because Logistic Regression requires numerical input, and TF-IDF effectively captures the semantic meaning of complaints by giving higher weight to distinctive words like "pothole", "garbage", etc.

### Q2: Why did you choose Logistic Regression over other algorithms?
**A:** Logistic Regression is simple, efficient, and works well with high-dimensional text data (after TF-IDF transformation). It's a great baseline model for text classification and provides interpretable results. We chose it over complex models like Deep Neural Networks because it's faster to train, easier to explain, and sufficient for our use case with 300+ samples.

### Q3: What is a stratified 80/20 train-test split?
**A:** It means 80% of data goes for training the model and 20% for testing its performance. The "stratified" part ensures that the proportion of categories (Pothole, Garbage, etc.) and priorities (Low, Medium, High) are preserved in both training and test sets. This prevents situations where the test set has completely different distribution than real-world data.

### Q4: Why can't we just train and test on the same data?
**A:** If we train and test on the same data, the model will just memorize the answers (this is called overfitting). When we give it a new complaint it hasn't seen before, it will fail completely. The train-test split ensures the model generalizes well to unseen data.

### Q5: What does accuracy tell us? Can we rely on it alone?
**A:** Accuracy tells us the percentage of predictions that are correct. However, it can be misleading with imbalanced datasets. For example, if 70% of complaints are "Pothole" and 30% are other categories, a "dummy" model that always predicts "Pothole" would have 70% accuracy but would be useless for other categories. This is why we also look at precision, recall, and F1 score.

### Q6: Explain Precision and Recall with a real example from our system.
**A:**
- **Precision:** If the model predicts 10 complaints as "Pothole", and 8 are actually potholes, precision is 80%. It measures: "Of all things the model called 'Pothole', how many are truly potholes?"
- **Recall:** If there are actually 15 pothole complaints in the test set, and the model finds 12 of them, recall is 80%. It measures: "Of all real pothole complaints, how many did the model catch?"

### Q7: What is the F1 score and why is it the harmonic mean?
**A:** F1 score is the harmonic mean of precision and recall. It gives a single number that balances both metrics. A model can have high precision but low recall (it's very careful and only predicts when very sure, but misses many real issues), or high recall but low precision (it predicts everything as the target class but gets many wrong). F1 prevents optimizing for just one metric at the expense of the other.

### Q8: What does a confusion matrix actually show?
**A:** A confusion matrix shows the complete breakdown of predictions vs. actual values. The diagonal shows correct predictions, and off-diagonal entries show where the model made mistakes. For example, if "Pothole" is often confused with "Drainage", that tells us we need more training examples that distinguish these two types of issues.

### Q9: Why is the dataset called "synthetic"?
**A:** The dataset is synthetic because it was artificially generated for this demo project, not collected from real civic systems. It contains 300+ realistic-style complaints balanced across categories and priorities, including some Hinglish wording, but the actual complaint data from cities would be very different in volume, language, and diversity.

### Q10: If the model predicts "Needs review" when confidence is below 40%, what happens then?
**A:** When the model's confidence in its category prediction is below 40%, we mark the issue as "Needs review" instead of assigning a category. This means a human admin must manually review and correct the category. This safety mechanism prevents incorrectly classified issues from going through the system unresolved.
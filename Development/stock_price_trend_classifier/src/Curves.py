# from sklearn.metrics import confusion_matrix
# import matplotlib.pyplot as plt
# import seaborn as sns

# cm = confusion_matrix(y_test, y_pred_rf)

# plt.figure()
# sns.heatmap(cm, annot=True, fmt="d")
# plt.title("Confusion Matrix - Random Forest")
# plt.xlabel("Predicted")
# plt.ylabel("Actual")
# plt.show()

importances = model_rf.feature_importances_

plt.figure()
plt.bar(X.columns, importances)
plt.title("Feature Importance - Random Forest")
plt.xticks(rotation=45)
plt.show()
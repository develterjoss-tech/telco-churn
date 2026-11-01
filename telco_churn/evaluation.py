from sklearn.metrics import average_precision_score, f1_score, recall_score, precision_score
from sklearn.metrics import accuracy_score, confusion_matrix


def evaluate_model(model, X , y ) :
    threshold = 0.5
    indice = list(model.classes_).index(1)

    pred_proba = model.predict_proba(X)

    scores = pred_proba[:,indice]
    pred_eval =[ 1 if score >= threshold else 0 for score in scores]


    accuracy = accuracy_score(y,pred_eval)
    f1 = f1_score(y,pred_eval,zero_division=0)
    recall = recall_score(y,pred_eval,zero_division=0)
    matrix = confusion_matrix(y,pred_eval,labels=[0,1])
    avg_precision = average_precision_score(y,scores)
    precision = precision_score(y,pred_eval,zero_division=0)

    return {
        "accuracy" : float(accuracy),
        "recall" : float(recall),
        "f1_score" : float(f1),
        "avg_precision" : float(avg_precision),
        "matrix_confusion" : matrix.tolist(),
        "precision" : float(precision),
        "threshold" : threshold
    }
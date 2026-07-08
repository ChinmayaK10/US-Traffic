import pandas as pd
import numpy as np
from dataclasses import dataclass
from src.utils.logger import logging
from src.utils.exception import CustomError
import sys
import os
from sklearn.metrics import classification_report,confusion_matrix
from src.utils.common import save_object
from xgboost import XGBClassifier
from sklearn.utils.class_weight import compute_sample_weight
@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join("artifacts","model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()

    def initiate_model_trainer(self,train_df,test_df):
        try:
            logging.info("Split training and test into input and output data")
            x_train=train_df.iloc[:,:-1]
            x_test=test_df.iloc[:,:-1]
            Y_train=train_df.iloc[:,-1]
            Y_test=test_df.iloc[:,-1]
            y_train_target = np.array(Y_train).ravel()
            y_test_target = np.array(Y_test).ravel()
            # Sample weights
            sample_weights = compute_sample_weight(class_weight="balanced",y=y_train_target)
            model = XGBClassifier(tree_method="hist",device="cuda",n_estimators=1000,learning_rate=0.02, max_depth=8, eval_metric="mlogloss",random_state=42)
            model.fit(x_train,y_train_target,sample_weight=sample_weights)
            y_pred=model.predict(x_test)
            Conf_mat=confusion_matrix(y_pred=y_pred,y_true=y_test_target)
            claass_report=classification_report(y_pred=y_pred,y_true=y_test_target)

            save_object(self.model_trainer_config.trained_model_file_path,
                        obj=model)
            
            return {'Confusion_matrix':Conf_mat,"Classification_report":claass_report}
        except Exception as e:
            raise CustomError(e,sys)
        
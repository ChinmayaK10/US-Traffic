import os 
import sys
from src.utils.exception import CustomError
from src.utils.logger import logging
import pandas as pd
import numpy as np
from src.utils.common import save_object
from dataclasses import dataclass
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
@dataclass
class DataTransformConfig:
    proccessor_obj_file_path=os.path.join('artifacts','preproccessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformConfig()
    def get_data_transformer_obj(self):
        try:
        
            numerical_feature=['Start_Lat', 'Start_Lng', 'Humidity(%)', 
                'Visibility(mi)','Temperature(C)', 'Start_hour', 'Start_minute',
                'Start_month','Start_day']
            categorical_feature=["Weather_Conditions","Severity"]

            numerical_pipeline=Pipeline(
            steps=[('Minmax',MinMaxScaler())]
            )
        
            categorical_pipeline=Pipeline(steps=[('Ohe',OneHotEncoder())])

            preprocesor=ColumnTransformer([
            ('numerical_pipeline',numerical_pipeline,numerical_feature),
            ('categorical_feature',categorical_pipeline,categorical_feature)
        ])

            return preprocesor
        except Exception as e:
            raise CustomError(e,sys)
    def initiate_data_transformation(self,train_path,test_path):
        try:
            logging.info('reading traina and test data')
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)
            
            preproccessor_obj=self.get_data_transformer_obj()
            target_feature='Congestion_Speed'
            logging.info("seperating X and Y")
            input_feature_train_df=train_df[['Start_Lat', 'Start_Lng', 'Humidity(%)', 
                'Visibility(mi)','Temperature(C)', 'Start_hour', 'Start_minute',
                'Start_month','Start_day',"Weather_Conditions","Severity"]]
            input_feature_test_df=test_df[['Start_Lat', 'Start_Lng', 'Humidity(%)', 
                'Visibility(mi)','Temperature(C)', 'Start_hour', 'Start_minute',
                'Start_month','Start_day',"Weather_Conditions","Severity"]]

            target_train_df=train_df[target_feature].map({'Fast':2,'Moderate':1,'Slow':0})
            target_test_df=test_df[target_feature].map({'Fast':2,'Moderate':1,'Slow':0})

            logging.info('preproccesing the data')
            input_preprocessed_train_df=preproccessor_obj.fit_transform(input_feature_train_df)
            input_preprocessed_test_df=preproccessor_obj.transform(input_feature_test_df)

            train_arr=np.c_[input_preprocessed_train_df,np.array(target_train_df)]
            test_arr=np.c_[input_preprocessed_test_df,np.array(target_test_df)]

            save_object(
                file_path=self.data_transformation_config.proccessor_obj_file_path,
                obj=preproccessor_obj
            )
           
            
            return (train_arr,test_arr,self.data_transformation_config.proccessor_obj_file_path)
        except Exception as e:
            raise CustomError(e,sys)
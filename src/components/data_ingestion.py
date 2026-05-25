import os 
import sys 
from src.utils.exception import CustomError
import pandas as pd
from src.utils.logger import logging
from sklearn.model_selection import train_test_split
from dataclasses import dataclass 
from src.components.data_trasnformation import DataTransformation
from src.components.model_traininig import ModelTrainer

@dataclass
class DataIngestionConfig:
    train_data_path:str=os.path.join('data','train.csv')
    test_data_path:str=os.path.join('data','test.csv')
    raw_data_path_data_path:str=os.path.join('data','us_congestion_2016_2022_sample_2m.csv')
class DataIngestion:
    def __init__(self):
        self.ingestion_config=DataIngestionConfig()
    def initiate_data_ingestion(self):
        logging.info('entered the data ingestion method')
        os.makedirs(os.path.dirname(self.ingestion_config.train_data_path),exist_ok=True)

        try:
            logging.info('reading the dataset as df')
            df=pd.read_csv(r'D:\ML project\US traffic\data\data_cleaned.csv')
            logging.info("splitting the data into train and test")
            train_data,test_data=train_test_split(df,test_size=0.25,random_state=42)
            train_data.to_csv(self.ingestion_config.train_data_path,header=True,index=False)
            test_data.to_csv(self.ingestion_config.test_data_path,header=True,index=False)
            logging.info('train test data done')

            return (self.ingestion_config.train_data_path,self.ingestion_config.test_data_path)
        except Exception as e:
                raise CustomError(e,sys)
if __name__=='__main__':
    di=DataIngestion()
    train_path,test_path=di.initiate_data_ingestion()

    dt=DataTransformation()
    train_arr,test_arr,preprocessor_patj=dt.initiate_data_transformation(test_path=test_path,train_path=train_path)

    model=ModelTrainer()
    (model.initiate_model_trainer(train_array=train_arr,test_array=test_arr))
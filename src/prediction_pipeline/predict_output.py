import sys
import pandas as pd
from src.utils.logger import logging
from src.utils.exception import CustomError
from src.utils.common import load_obj
import os
class CustomData:

    def __init__(
        self,
        Start_Lat: float,
        Start_Lng: float,
        Humidity: float,
        Visibility: float,
        Temperature: float,
        Start_hour: int,
        Start_minute: int,
        Start_month: int,
        Start_day: int,
        Weather_Conditions: str,
        Severity: int
    ):

        self.Start_Lat = Start_Lat

        self.Start_Lng = Start_Lng

        self.Humidity = Humidity

        self.Visibility = Visibility

        self.Temperature = Temperature

        self.Start_hour = Start_hour

        self.Start_minute = Start_minute

        self.Start_month = Start_month

        self.Start_day = Start_day

        self.Weather_Conditions = (
            Weather_Conditions
        )

        self.Severity = Severity

    def get_datas_as_df(self):
     try:

        logging.info(
            "converting predicting data"
        )

        custom_data_input_df = {

            'Start_Lat': [self.Start_Lat],

            'Start_Lng': [self.Start_Lng],

            "Humidity(%)": [self.Humidity],

            'Visibility(mi)': [self.Visibility],

            'Temperature(C)': [self.Temperature],

            'Start_hour': [self.Start_hour],

            'Start_minute': [self.Start_minute],

            'Start_month': [self.Start_month],

            'Start_day': [self.Start_day],

            "Weather_Conditions": [
                self.Weather_Conditions
            ],

            "Severity": [
                self.Severity
            ],
        }

        return pd.DataFrame(
            custom_data_input_df
        )

     except Exception as e:
        raise CustomError(
            e,
            sys
        )
        
class PredictionPipeline:
    def __init__(self):
        pass
    
    def predict(self,features):
        try:
            model_path=os.path.join("artifacts",'model.pkl')
            preprocessor_path=os.path.join('artifacts','preproccessor.pkl')
            logging.info("Loading the model")
            model=load_obj(file_path=model_path)
            preprocessor=load_obj(preprocessor_path)

            data_scaled=preprocessor.transform(features)
            preds=model.predict(data_scaled)
            return preds
        except Exception as e:
             raise CustomError(e,sys)
            
import requests
import redis
from datetime import datetime, timedelta
import pandas
import pathlib
import glob
import json
import urllib.request 
import pickle
class Data_Manager:
    def __init__(self):
        # connect to redis
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.redis_client_model = redis.Redis(host='localhost', port=6379, decode_responses=False)
        urllib.request.urlretrieve("https://raw.githubusercontent.com/dssg-pt/covid19pt-data/master/data_concelhos_new.csv", "data_concelhos.csv")

    def update_data(self):
        self.update_covidpt_data()
        self.update_patients_data()
        self.update_concelhos_data()

    def update_covidpt_data(self):
        #client.delete('covidPTAPI')

        # get a value
        value = self.redis_client.get('covidPTAPI')
        
        
        if value=="" or value == None:
            #full dataset route
            dateStr = datetime.now() - timedelta(days=1)
            dateStr= datetime.strftime(dateStr,"%d-%m-%Y")
            route="get_entry/26-02-2020_until_"+dateStr
        else:
            #differential route
            dateStr = datetime.now() + timedelta(days=1)
            dateStr= datetime.strftime(dateStr,"%d-%m-%Y")
            dateFirst = self.redis_client.get('covidPTAPI_LASTUPDATE')
            route="get_entry/"+dateFirst+"_until_"+dateStr

        old_dataframe_covidpt = self.redis_client.get('covidPTAPI')
        #print(old_dataframe_covidpt)
        if old_dataframe_covidpt!="" and old_dataframe_covidpt != None:
            json_old_dataframe_covidpt = json.loads(old_dataframe_covidpt)
            old_dataframe_covidpt = pandas.DataFrame.from_dict(json_old_dataframe_covidpt, orient="index")
        else:
            old_dataframe_covidpt = pandas.DataFrame()

        new_dataframe_covidpt = pandas.DataFrame.transpose(old_dataframe_covidpt)
        req = requests.get('https://covid19-api.vost.pt/Requests/'+route)
        #print(req.text)
        if req.text!="" and req.text!="At least one of the dates was not found.":
            differential_dataframe_covidpt = json.loads(req.text)
            differential_dataframe_covidpt = pandas.DataFrame.from_dict(differential_dataframe_covidpt, orient="index")
            differential_dataframe_covidpt = pandas.DataFrame.transpose(differential_dataframe_covidpt)

        # only append if the day doesnt already exist
        if datetime.strftime(datetime.now(),"%d-%m-%Y")!=self.redis_client.get('covidPTAPI_LASTUPDATE') and req.text!="" and req.text!="At least one of the dates was not found.":
            new_dataframe_covidpt=new_dataframe_covidpt.append(differential_dataframe_covidpt)
       
       
        #print(new_dataframe_covidpt)
        self.covidpt_data = new_dataframe_covidpt
        # set a key
        self.redis_client.set('covidPTAPI',new_dataframe_covidpt.to_json())
        
        self.redis_client.delete('covidPTAPI_LASTUPDATE')
        self.redis_client.set('covidPTAPI_LASTUPDATE',str(datetime.strftime(datetime.now(),"%d-%m-%Y")))
       
    def update_patients_data(self):
        all_files = glob.glob(str(pathlib.Path(__file__).parent.absolute())+'\\patients_data\\*.csv')

        li = []

        for filename in all_files:
            df = pandas.read_csv(filename, index_col=None, header=0)
            li.append(df)
        frame = pandas.concat(li, axis=0, ignore_index=True)

        frame = self.clean_patients_data(frame)

        self.redis_client.set('covidPatientsData',frame.to_json())
        value = self.redis_client.get('covidPatientsData')
        
        df = pandas.read_json(value)
        pandas.set_option('display.max_column',None)

        self.patients_data = frame

    def update_concelhos_data(self):
        self.concelhos_data = pandas.read_csv("data_concelhos.csv", index_col=None, header=0)

    def clean_patients_data(self, df):
        #Remove Invalid Test Results
        df.drop(df.loc[(df['covid19_test_results'] != 'Negative') & (df['covid19_test_results'] != 'Positive')].index, inplace=True)

        #Remove Rapid Tests
        df.drop(df.loc[(df['test_name'] == 'Rapid COVID-19 PCR Test')].index, inplace=True)

        symptoms = ["labored_respiration","cough","fever","fatigue","headache","loss_of_smell","loss_of_taste","muscle_sore","sore_throat"]
        other_factors = ["high_risk_interactions"]
        columns = ["covid19_test_results", "age"] + symptoms + other_factors
        
        df = df[columns]
        
        covid19_test_results = {'Positive': 1, 'Negative': 0}
        factor_to_boolean = {True: int(1), False: int(0)}
        
        df["covid19_test_results"] = df["covid19_test_results"].map(covid19_test_results)
        
        for symptom in symptoms:
            df[symptom] = df[symptom].map(factor_to_boolean)
        
        for factor in other_factors:
            df[factor] = df[factor].map(factor_to_boolean)
        return df

    def get_patients_data(self):
        print(self.patients_data.columns.values)
        return self.patients_data

    def get_covidpt_data(self):
        return self.covidpt_data
    
    def get_portugal_population(self):
        primeira_segunda = self.concelhos_data.tail(1)["data"].iloc[0]
        return self.concelhos_data.loc[self.concelhos_data['data'] == primeira_segunda]['population'].sum()
        
    def get_concelho_data(self,concelho):
        data = self.concelhos_data.loc[self.concelhos_data['concelho'] == concelho].tail(1)
        return data["densidade_populacional"].iloc[0],data["population"].iloc[0],data["confirmados_14"].iloc[0],data["incidencia"].iloc[0]

    def store_trained_model(self,model):
        self.redis_client_model.set('trainedModel',pickle.dumps(model))
        self.redis_client.delete('trainedModel_LASTUPDATE')
        self.redis_client.set('trainedModel_LASTUPDATE',str(datetime.strftime(datetime.now(),"%d-%m-%Y")))

    def get_trained_model_updated_date(self):
        return self.redis_client.get('trainedModel_LASTUPDATE')
    
    def get_trained_model(self):
        print("###")
        model = self.redis_client_model.get('trainedModel')
        print("###")
        return pickle.loads(model)
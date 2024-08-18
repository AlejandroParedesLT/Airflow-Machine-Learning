# Alejandro Paredes La Torre

import datetime
from dateutil.relativedelta import relativedelta

# Data analysis
import pyodbc
import numpy as np
import pandas as pd
import statsmodels.api as sm
from numpy import unique
from numpy import where

from dateutil.relativedelta import relativedelta

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, normalize
import joblib


class default_credit_risk():
    def __init__(self
                 , input_date
                 , df_DEMOGRAFICO
                 , df_bienes
                 , df_captaciones
                 , df_captaciones_l90
                
                ):
        self.fecha_corte = input_date
        self.df_DEMOGRAFICO = df_DEMOGRAFICO
        self.df_bienes = df_bienes
        self.df_captaciones = df_captaciones
        self.df_captaciones_l90 = df_captaciones_l90
        
        
        self.date_b_year = (self.fecha_corte - relativedelta(months=11)).replace(day=1)
        self.date_b_2yearAgo = (self.date_b_year - relativedelta(months=24)).replace(day=1)
        self.date_b_lq = (self.fecha_corte - relativedelta(months=2)).replace(day=1)
        self.date_b_l60 = (self.fecha_corte - relativedelta(months=1)).replace(day=1)
        self.date_b_ls = (self.fecha_corte - relativedelta(months=5)).replace(day=1)
        self.date_b_fc = self.fecha_corte.replace(day=1)
   
    def calculate_measure(self
                          ,df#:pd.DataFrame
                          , date_filter_column#:datetime.date
                          , date_inic#:datetime.date
                          , date_fin#:datetime.date
                          , groupby_fields#:list
                          , aggregation_fields
                          , suffix_name):#:list) -> pd.DataFrame:

        aggregation = {field_name: measure for final_name, field_name, measure in aggregation_fields}
        #desired_names = {field_name: final_name for final_name, field_name, measure in aggregation_fields}
        desired_names = []
        for final_name, field_name, measure in aggregation_fields:
            desired_names = desired_names+final_name
        #desired_names = list(reversed([name_ if suffix_name is None else name_+'_'+suffix_name for name_ in desired_names]))
        desired_names = [name_ if suffix_name is None else name_+'_'+suffix_name for name_ in desired_names]

        
        #print(aggregation)

        if not groupby_fields:
            raise ValueError("Invalid groupby_fields")
        if not aggregation_fields:
            raise ValueError("Invalid aggregation_fields")
        if not aggregation_fields and not groupby_fields:
            raise ValueError("Invalid groupby_fields and aggregation_fields")
        
        filtered_df = df[
            (df[date_filter_column] >= date_inic) &
            (df[date_filter_column] <= date_fin)
            ]
        measure = filtered_df.groupby(groupby_fields, as_index=False).agg(aggregation)
        print(measure.head())
        #measure.columns =  ['_'.join(col) for col in measure.columns]
        #print(measure.head())
        measure.columns = groupby_fields+desired_names
        print(measure.head())
        return measure

    # Transformations ........

    def main_join(  self
                    , fact_saldos
                    , dim_demograph
                    , dim_declaracion
                    , measure_captac_ly
                    , measure_captac_lq
                    , measure_captac_l30
                    , measure_captac_l90
                    , measure_EIF_l90
                    , measure_EIF_ly
                    , measure_SCORE_lq
                    , measure_paymentplan_lm
                    , measure_paymentplan_lq
                    , measure_paymentplan_ls
                    , measure_paymentplan_ly
                    , measure_payment_lm
                    , measure_payment_lq
                    , measure_payment_ly
                    , measure_cambioRubro_lq
                    , measure_cambioRubro_ly
                    , measure_cambioRubro_h
            ):
            df_snapshot = fact_saldos.merge(
                            dim_demograph,  left_on = 'NUMEROPERSONA', right_on='NUMEROPERSONA', how = 'left'
                    ).merge(
                            dim_declaracion, left_on = 'NUMEROPERSONA', right_on='NUMEROPERSONA', how = 'left'
                    ).merge(
                            measure_captac_ly, left_on = 'NUMEROPERSONA', right_on='NUMEROPERSONA', how = 'left'
                    ).merge(
                            measure_captac_lq, left_on = 'NUMEROPERSONA', right_on='NUMEROPERSONA', how = 'left'
                    ).merge(
                            measure_captac_l30, left_on = 'NUMEROPERSONA', right_on='NUMEROPERSONA', how = 'left'
                    ).merge(
                            measure_captac_l90, left_on = 'NUMEROPERSONA', right_on='NUMEROPERSONA', how = 'left'
                    ).merge(
                            measure_EIF_l90, left_on = 'numerodocumento', right_on='numerodocumento', how = 'left'
                    ).merge(
                            measure_EIF_ly, left_on = 'numerodocumento', right_on='numerodocumento', how = 'left'
                    ).merge(
                            measure_SCORE_lq, left_on = 'NUMEROPERSONA', right_on='NUMEROPERSONA', how = 'left'
                    ).merge(
                            measure_paymentplan_lm, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_paymentplan_lq, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_paymentplan_ls, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_paymentplan_ly, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_payment_lm, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_payment_lq, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_payment_ly, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_cambioRubro_lq, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_cambioRubro_ly, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    ).merge(
                            measure_cambioRubro_h, left_on = 'jts_oid', right_on='jts_oid', how = 'left'
                    )
            df_snapshot.set_index('jts_oid', inplace=True)
            return df_snapshot

    def standarized_df(self, df):
        imputer = SimpleImputer()
        df_cleaned = pd.DataFrame(imputer.fit_transform(df), columns = df.columns, index=df.index)

        scaler=StandardScaler()
        X_std=pd.DataFrame(scaler.fit_transform(df_cleaned), columns = df_cleaned.columns, index=df_cleaned.index)
        X = pd.DataFrame(normalize(X_std,norm='l2') , columns = df_cleaned.columns, index=df_cleaned.index)
        return X_std
    
    def prediction(self):
        self.configuration()
        dim_demograph, dim_declaracion = self.dimensiones()
        measure_captac_ly, measure_captac_lq, measure_captac_l30, measure_captac_l60 = self.captaciones_fact()
        measure_EIF_l90, measure_EIF_ly, measure_SCORE_lq = self.eif_fact()
        measure_paymentplan_lm, measure_paymentplan_lq, measure_paymentplan_ls, measure_paymentplan_ly = self.paymentplan_fact()
        measure_payment_lm, measure_payment_lq, measure_payment_ly = self.payment()
        measure_cambioRubro_lq, measure_cambioRubro_ly, measure_cambioRubro_h = self.cambioRubro()
        fact_saldos = self.fact_saldos()
        df_snapshot = self.main_join(
                        fact_saldos
                        , dim_demograph
                        , dim_declaracion                        
                        , measure_captac_ly
                        , measure_captac_lq
                        , measure_captac_l30
                        , measure_captac_l60
                        , measure_EIF_l90
                        , measure_EIF_ly
                        , measure_SCORE_lq
                        , measure_paymentplan_lm
                        , measure_paymentplan_lq
                        , measure_paymentplan_ls
                        , measure_paymentplan_ly
                        , measure_payment_lm
                        , measure_payment_lq
                        , measure_payment_ly                        
                        , measure_cambioRubro_lq
                        , measure_cambioRubro_ly
                        , measure_cambioRubro_h
                        )
        
        del dim_demograph, dim_declaracion, measure_captac_ly, measure_captac_lq, measure_captac_l30, measure_captac_l60
        del measure_EIF_l90, measure_EIF_ly
        del measure_paymentplan_lm, measure_paymentplan_lq, measure_paymentplan_ls, measure_paymentplan_ly
        del measure_payment_lm, measure_payment_lq, measure_payment_ly
        del measure_cambioRubro_lq, measure_cambioRubro_ly, measure_cambioRubro_h

        print('Df Snapshot conolidado')
        print(df_snapshot.head())
        
        df_snapshot = df_snapshot.drop(['NUMEROPERSONA', 'numerodocumento'], axis=1).replace(np.nan, 0)
        df_snapshot.columns = df_snapshot.columns.astype(str).str.replace(" ", "_")

        model = joblib.load('./ml_model/default_credit_risk/default_credit_risk.joblib')

        f_names = model.feature_names_in_
        y_pred = model.predict(self.standarized_df(df_snapshot[f_names]))
        y_prob = model.predict_proba(self.standarized_df(df_snapshot[f_names]))

        df_predict = pd.DataFrame(y_pred, columns=['pure_predictions'], index = df_snapshot.index)
        df_probabilities = pd.DataFrame(y_prob, columns=['probabilities_zero','probabilities_one'], index = df_snapshot.index)

        df_results = df_predict.merge(df_probabilities, left_index=True, right_index=True, how = 'inner').merge(df_snapshot[['dias_mora', 'sum_days_atraso_lq']], left_index=True, right_index=True, how = 'inner')

        df_results['fecha_predict'] = self.fecha_corte
        df_results.reset_index(inplace=True)
        print("Resultados Prediccion")
        print(df_results.head())
        return (df_results.loc[:, df_results.columns!='sum_days_atraso_lq'])

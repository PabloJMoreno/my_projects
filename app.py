from pycaret.regression import load_model, predict_model
import streamlit as st
import pandas as pd
import numpy as np

modelo = load_model('clientes_gbr_088')

def predict(model, input_df):
    predictions_df = predict_model(estimator=model, data=input_df)
    predictions = predictions_df['prediction_label'][0]
    return predictions

def run():
    from PIL import Image
    image = Image.open('oip.jpg')
    image_company = Image.open('logo.png')

    st.image(image, use_column_width=False)

    add_selectbox = st.sidebar.selectbox(
    "Cómo quiere hacer la predicción?", 
    ("Online", "Batch"))

    st.sidebar.info('Esta apliacion hace una predicción de los gastos hospitalarios de un posible paciente')
    st.sidebar.success('https://sumamoos.com')
    
    st.sidebar.image(image)

    st.title("App de Predicción de Gastos Medicos")

    if add_selectbox == 'Online':
        edad = st.number_input('edad', min_value=1, max_value=100, value=25)
        genero = st.selectbox('genero', ['femenino', 'masculino'])
        imc = st.number_input('imc', min_value=10, max_value=50, value=10)
        hijos = st.selectbox('hijos', [0,1,2,3,4,5,6,7,8,9,10])
        if st.checkbox('fumador'):
            fumador = 'si'
        else:
            fumador = 'no'
        region = st.selectbox('region', ['sur', 'oeste', 'norte', 'este'])
        
        output=""
        
        input_dict = {'edad' : edad, 'genero' : genero, 'imc' : imc, 'hijos' : hijos, 'fumador' : fumador, 'region' : region}
        input_df = pd.DataFrame([input_dict])
        
        if st.button("Prediccion"):
            output = predict(model=modelo, input_df=input_df)
            output = '$ ' + str(output)
            
        st.success('El resultado es {}'.format(output))
        
    if add_selectbox == 'Batch':
        file_upload = st.file_uploader("Cargar archivo csv para predicciones", type=["csv"])
        
        if file_upload is not None:
            data = pd.read_csv(file_upload)
            predictions = predict_model(estimator=modelo, data=data)
            st.write(predictions)

if __name__=='__main__':
    run()
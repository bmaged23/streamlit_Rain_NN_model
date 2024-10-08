import streamlit as st
import joblib
import pandas as pd
import numpy as np
#streamlit run streamlit_app.py

st.set_page_config(
    page_title="K-means Prediction",
    page_icon=":0"
)

# Load the KMeans model, scaler, and encoders
model = joblib.load('NN_model.pkl')
label_encoders = joblib.load('label_encoders.pkl')  # Ensure this is a dictionary of LabelEncoders
scale = joblib.load('scaler.pkl')

# File uploader
file = st.file_uploader("Upload the file: ", type=["csv", "xlsx"])
df = None

if file is not None:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
        

    #Date=df.select_dtypes(include="Date")
    if df is not None:
        st.write(df.head())
        IQR_interval=[[-6.35, 30.849999999999998], [2.2999999999999954, 43.900000000000006], [-1.2000000000000002, 2.0], [-3.8139780972602635, 13.488386858356158], [-1.5891839597562303, 16.79351037585374], [5.5, 73.5], [-11.0, 37.0], [-3.5, 40.5], [18.0, 122.0], [-6.5, 109.5], [1000.65, 1034.65], [998.0, 1032.4], [-4.172820848873743, 13.703692509324245], [-2.048021563042129, 11.413369271736881], [-1.6500000000000004, 35.550000000000004], [1.7500000000000036, 41.349999999999994]]
        columnss =[  'MinTemp', 'MaxTemp', 'Rainfall', 'Evaporation',
            'Sunshine', 'WindGustSpeed',
            'WindSpeed9am', 'WindSpeed3pm', 'Humidity9am', 'Humidity3pm',
            'Pressure9am', 'Pressure3pm', 'Cloud9am', 'Cloud3pm', 'Temp9am',
            'Temp3pm']
        for column,(lower_bound,upper_bound) in zip(columnss,IQR_interval):
            outliers_lower = df[column] < lower_bound
            outliers_upper = df[column] > upper_bound
            df.loc[outliers_lower, column] = lower_bound
            df.loc[outliers_upper, column] = upper_bound
        
        
        y=df["RainTomorrow"]
        columns_to_drop = ['Temp9am', 'Pressure3pm', 'MaxTemp', 'Rainfall', 'Temp3pm','Unnamed: 0','RainTomorrow'] 
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')
        df["Date"] = label_encoders["Date"].transform(df["Date"])
        df["Date"]=df["Date"].astype("float32")
        obj_col = df.select_dtypes(include="object").columns.tolist()
        print(obj_col)
        num_col =[  'MinTemp', 'Evaporation',
            'Sunshine', 'WindGustSpeed',
            'WindSpeed9am', 'WindSpeed3pm', 'Humidity9am', 'Humidity3pm',
            'Pressure9am', 'Cloud9am', 'Cloud3pm','Date'
            ]
        df[num_col] = scale.transform(df[num_col])
        if obj_col:
            for col in obj_col:
                if col in obj_col:
                    try:
                        if col in label_encoders:
                            df[col] = label_encoders[col].transform(df[col])
                        else:
                            st.error(f"No encoder found for column: {col}")
                            st.stop()
                    except KeyError:
                        st.error(f"No encoder found for column: {col}")
                        st.stop()
                    except ValueError as e:
                        st.error(f"Error in encoding column {col}: {e}")
                        st.stop()
            try:
                prediction = model.predict(df)
                pred_acc = ["Yes" if p > 0.5 else "No" for p in prediction]


                pred = ["Rain" if p > 0.5 else "No Rain" for p in prediction]
                
                if len(pred) > 1:
                    accuracy = np.sum(np.array(pred_acc) == y) / len(y)
                    st.write("accuracy= ", accuracy)
                    
                    # Assign the list directly
                    st.session_state.text_list = pred
                    st.write("Predicted Classes:")
                    st.write(st.session_state.text_list)
                else:
                    st.write(f"Predicted Class: {pred[0]}")
            except ValueError as e:
                st.error(f"Error in prediction: {e}")
                st.stop()


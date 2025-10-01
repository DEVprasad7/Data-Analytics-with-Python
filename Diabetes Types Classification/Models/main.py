from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

scaler = StandardScaler()


rf_model = joblib.load('model1.pkl')
logistic_model = joblib.load('model2.pkl')

def get_input(prompt, type_=int):
    return type_(input(prompt))

def one_hot_encode(value, categories):
    return [1 if i == value else 0 for i in range(categories)]

# Collect numeric inputs
print("====Diabetes Prediction System====")
print("Please provide the following health metrics:")
Age = get_input("Enter Age(5-79): ")
BMI = get_input("Enter BMI(15-39): ")
Insulin_Levels = get_input("Enter Insulin Levels (5-49): ")
Blood_Pressure = get_input("Enter Blood Pressure (90-149): ")
Blood_Glucose_Levels = get_input("Enter Blood Glucose Levels (100-199): ")
Smoking_Status = get_input("Do you smoke? (1 for Yes, 0 for No): ")
Family_History = get_input("Do you have a family history of diabetes? (1 for Yes, 0 for No): ")

# One-hot encode categorical inputs
Alcohol_Consumption = get_input("How often do you drink alcohol? (0:Low, 1:Moderate, 2:High): ")
Alcohol_Consumption_encoded = one_hot_encode(Alcohol_Consumption, 3)

Physical_Activity = get_input("Rate Your Physical Activity (0:Low, 1:Moderate, 2:High): ")
Physical_Activity_encoded = one_hot_encode(Physical_Activity, 3)
scaler.fit_transform([[Age, BMI, Insulin_Levels, Blood_Pressure, Blood_Glucose_Levels, 
               Smoking_Status, Family_History, *Alcohol_Consumption_encoded, *Physical_Activity_encoded]])
# Combine all inputs
input_data = [[Age, BMI, Insulin_Levels, Blood_Pressure, Blood_Glucose_Levels, 
               Smoking_Status, Family_History, *Alcohol_Consumption_encoded, *Physical_Activity_encoded]]



# Make predictions
pre_rf = rf_model.predict(input_data)
pre_lr = logistic_model.predict(scaler.transform(input_data))

def predictions(x):
    return ["Prediabetic", "Type 1 Diabetic", "Type 2 Diabetic"][x]

print("\n")
print("\n====Prediction Results====")
print("\n")

print(f"Random Forest Model Prediction : {predictions(pre_rf[0])}")
print("\n")
print(f"Logistic Regression Model Prediction : {predictions(pre_lr[0])}")

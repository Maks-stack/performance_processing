import pandas as pd
import numpy as np
from datetime import datetime

encoding = 'utf-8-sig'

pd.options.display.width = 5000
pd.set_option('display.max_columns', None)
pd.options.display.max_colwidth = 5000

users = pd.read_csv('usuarios.csv', usecols=["nombre","id_user"], encoding=encoding,engine='python', sep=";")
allUsers = pd.read_csv('allusers.csv', encoding=encoding, engine='python', sep=";")

users = pd.merge(users, allUsers, left_on="nombre", right_on="username")

users = users.drop('username',axis=1)

plan_data =pd.read_csv('planes_trabajo_templates.csv', encoding=encoding, engine='python', sep=";")
plan_data.drop(['icon', 'sexo', 'apellidos','estudios_oficiales','enviarInformacionEmail', 'terminosAceptados', 'password', 'reset_pass','timestamp','activacion', 'participarEstudios', 'evaluation_stage','edad', 'aceso_datos', 'email'], axis=1, inplace=True)

pruebaDict = {
  "prueba_1": "Reproduczca el dibujo",
  "prueba_3": "Fichas 2",
  "prueba_4": "reconozca la figura",
  "prueba_9": "Anagramas",
  "prueba_17": "asociando las parejas",
  "prueba_18": "encuentre las secuencia",
  "prueba_21": "Recordando las cartas",
}

prueba1 = pd.read_csv("pruebaData/prueba_1.csv", usecols=["nombre","id_user","id_partida", "aciertos","fallos","tiempo", "fecha", "dificultad"], encoding=encoding, engine='python',sep=";")
prueba21 = pd.read_csv("pruebaData/prueba_21.csv", usecols=["nombre","id_user","id_partida", "aciertos","fallos","tiempo", "fecha", "dificultad"], encoding=encoding, engine='python',sep=";")

def processPruebaDataFecha (pruebaData):
    pruebaData = pruebaData[pruebaData["aciertos"] != -1]
    pruebaData["fecha"] = pd.to_datetime(pruebaData["fecha"])
    pruebaData["performance"] = -1
    return pruebaData

prueba1 = processPruebaDataFecha(prueba1)
prueba21 = processPruebaDataFecha(prueba21)

columns= []

columns.append("Usuario")

# for name, planGroup in plan_data.groupby(['name']):
    
#     prueba2_group = planGroup.groupby(['prueba_name']).get_group("prueba_2")
    
#     planRow = prueba2_group.iloc[0]
#     print(planRow)
#     columns.append(planRow["name"] + " Nivel " + str(planRow["nivel"]) + "\n" + planRow["prueba_name"] + "mejor tiempo de " + str(planRow["repetitions"]))
#     columns.append(planRow["name"] + " Nivel " + str(planRow["nivel"]) + "\n" + planRow["prueba_name"] + "mejor fallos de " + str(planRow["repetitions"]))
#     columns.append(planRow["name"] + " Nivel " + str(planRow["nivel"]) + "\n" + planRow["prueba_name"] + "mejor tiempo de todos")
#     columns.append(planRow["name"] + " Nivel " + str(planRow["nivel"]) + "\n" + planRow["prueba_name"] + "mejor fallos de todos")

activityValues = pd.DataFrame(columns=columns)

def minMaxScaling(column):
    return (column-column.min())/(column.max()-column.min())
        
def processPlan (planName, pruebaName, displayName, pruebaData_byUser ): 
    
    global activityValues
    prueba2_dataByUser = pruebaData_byUser
    global groupedPlanDataByPlanName
    
    planDataSemana = groupedPlanDataByPlanName.get_group(planName) 
    
    nivel = planDataSemana.iloc[0]["nivel"]
    
    prueba2_dataByUser_semana = prueba2_dataByUser.query('dificultad == "Nivel ' + str(nivel) +"\"")
    prueba2_dataByUser_semana = prueba2_dataByUser_semana.sort_values(by='fecha')

    for iReps, repRow in prueba2_dataByUser_semana.iterrows():
        #print((100*repRow["fallos"]+10*repRow["tiempo"]))
        prueba2_dataByUser_semana.loc[prueba2_dataByUser_semana["id_partida"] == repRow["id_partida"], "performance"] = (100*repRow["fallos"]+10*repRow["tiempo"]) 
        
    if(len(prueba2_dataByUser_semana) > 1):        
        prueba2_dataByUser_semana["normalizedAndFlippedPerformance"] = 1 - minMaxScaling(prueba2_dataByUser_semana["performance"])
    else:    
        prueba2_dataByUser_semana["normalizedAndFlippedPerformance"] = 1

    #Recordando las cartas
    numberOfRepetitionsRequired = planDataSemana.query("prueba_name == '"+ pruebaName + "'")["repetitions"].iloc[0]
    firstRepetitions = prueba2_dataByUser_semana.head(numberOfRepetitionsRequired)
     
    if(len(firstRepetitions) > 0): 
        bestRepOutOfRequired = pd.Series()
        try:
            bestRepOutOfRequired = firstRepetitions.iloc[int(firstRepetitions["normalizedAndFlippedPerformance"].idxmax())]
        except:
            bestRepOutOfRequired = firstRepetitions.iloc[0]
        
        bestRepOutofAll = pd.Series()
        try:    
            bestRepOutofAll = prueba2_dataByUser_semana.loc[prueba2_dataByUser_semana["normalizedAndFlippedPerformance"].idxmax()]
        except:
            bestRepOutofAll = prueba2_dataByUser_semana.iloc[0]
            
        meanErrorFirstReps = firstRepetitions["fallos"].mean()
        meanErrorAll = prueba2_dataByUser_semana["fallos"].mean()
        
        deviationErrorFirstReps = firstRepetitions['fallos'].std() 
        deviationErrorAll = prueba2_dataByUser_semana['fallos'].std() 
        
        meanTimeFirstReps = firstRepetitions["tiempo"].mean()
        meanTimeAll = prueba2_dataByUser_semana["tiempo"].mean()
        
        deviationTimeFirstReps = firstRepetitions['tiempo'].std() 
        deviationTimeAll = prueba2_dataByUser_semana['tiempo'].std() 
        
        new_row[planName + "\n" + displayName + "\n" + " mejor tiempo de " + str(numberOfRepetitionsRequired)] = bestRepOutOfRequired["tiempo"]
        new_row[planName + "\n" + displayName + "\n" + " mejor fallos de " + str(numberOfRepetitionsRequired)] = bestRepOutOfRequired["fallos"]
        new_row[planName + "\n" + displayName + "\n" + " mean error de " + str(numberOfRepetitionsRequired)] = meanErrorFirstReps
        new_row[planName + "\n" + displayName + "\n" + " mean time de " + str(numberOfRepetitionsRequired)] = meanTimeFirstReps
        new_row[planName + "\n" + displayName + "\n" + " error deviation de " + str(numberOfRepetitionsRequired)] = deviationErrorFirstReps
        new_row[planName + "\n" + displayName + "\n" + " time deviation de " + str(numberOfRepetitionsRequired)] = deviationTimeFirstReps

        #ALL
        new_row[planName + "\n" + displayName + "\n" + " mejor tiempo de todos"] = bestRepOutofAll["tiempo"]
        new_row[planName + "\n" + displayName + "\n" + " mejor fallos de todos"] = bestRepOutofAll["fallos"]
        new_row[planName + "\n" + displayName + "\n" + " mean error todos"] = meanErrorAll
        new_row[planName + "\n" + displayName + "\n" + " mean time todos"] = meanTimeAll
        new_row[planName + "\n" + displayName + "\n" + " error deviation todos "] = deviationErrorAll
        new_row[planName + "\n" + displayName + "\n" + " time deviation todos"] = deviationTimeAll
                   
 # LOOP OVER USERS HERE ---------------------
for iUsers, userRow in users.iterrows():
    
    # if(iUsers > 0):
    #     break
    
    # #get first user here for debug
    # #userRow = users.iloc[2]
    # userRow = users.query('id_user ==' + str(338)).iloc[0]
    
    new_row = pd.DataFrame([{"Usuario": userRow["nombre"]}])

    groupedPlanDataByPlanName = plan_data.query('user_id ==' + str(userRow["id_user"])).groupby(plan_data['name'])

    for planName, group in groupedPlanDataByPlanName:
        
        for prueba in pruebaDict:
            loaded_pruebaData = pd.read_csv("pruebaData/" + prueba +".csv", usecols=["nombre","id_user","id_partida", "aciertos","fallos","tiempo", "fecha", "dificultad"], encoding=encoding, engine='python',sep=";")
            processPlan(planName, prueba, pruebaDict[prueba], loaded_pruebaData.query('id_user ==' + str(userRow["id_user"])))
    
    print(userRow["id_user"])        
    activityValues = activityValues.append(new_row, ignore_index=True, sort=False)            

#--------end loop over users

activityValues = activityValues.round(decimals=4)

activityValues.to_csv('output.csv', decimal=',', sep=";")
print("DONE---------------")
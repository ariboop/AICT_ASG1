from model import model
from pgmpy.inference import VariableElimination

# Create inference object
inference = VariableElimination(model)


#Inference 1
result_crowd1 = inference.query(variables=['Crowding Risk'], evidence={'Weather': 'Heavy','Day Type':'Weekday','Service Status':'Disrupted'})
# Print predictions for each node
print("Given a Very Rainy Weekday with Disrupted Service:")
print("Crowd")
for i, state in enumerate(result_crowd1.state_names['Crowding Risk']):
    print(f"    {state}: {result_crowd1.values[i]:.4f}")




print('\n\n')



# Inference 2
result_crowd2 = inference.query(variables=['Crowding Risk'], evidence={'Weather': 'None','Day Type':'Weekend','Service Status':'Normal'})
# Print predictions for each node
print("Given a Clear Weekend with Normal Service:")
print("Crowd")
for i, state in enumerate(result_crowd2.state_names['Crowding Risk']):
    print(f"    {state}: {result_crowd2.values[i]:.4f}")




print('\n\n')



# Inference 3
result_crowd3 = inference.query(variables=['Crowding Risk'], evidence={'Demand Proxy': 'High','Weather':'Heavy','Service Status':'Normal'})
# Print predictions for each node
print("Given a Rainy Day with Normal Service and High Demand:")
print("Crowd")
for i, state in enumerate(result_crowd3.state_names['Crowding Risk']):
    print(f"    {state}: {result_crowd3.values[i]:.4f}")




print('\n\n')




# Inference 4
result_crowd4 = inference.query(variables=['Crowding Risk'], evidence={'Weather': 'None','Day Type':'Weekend','Service Status':'Normal','Network Mode':'Today'})
# Print predictions for each node
print("Given a Clear Weekend with Normal Service (Today Mode):")
print("Crowd")
for i, state in enumerate(result_crowd4.state_names['Crowding Risk']):
    print(f"    {state}: {result_crowd4.values[i]:.4f}")




print('\n')



# Inference 5
result_crowd5 = inference.query(variables=['Crowding Risk'], evidence={'Weather': 'None','Day Type':'Weekend','Service Status':'Normal','Network Mode':'Today'})
# Print predictions for each node
print("Given a Clear Weekend with Normal Service (Future Mode):")
print("Crowd")
for i, state in enumerate(result_crowd5.state_names['Crowding Risk']):
    print(f"    {state}: {result_crowd5.values[i]:.4f}")





print('\n\n')



# Inference 6
result_crowd6 = inference.query(variables=['Crowding Risk'], evidence={'Weather': 'Heavy','Day Type':'Weekday','Service Status':'Reduced','Network Mode':'Today'})
# Print predictions for each node
print("Given a Rainy Weekday with Disrupted Service (Today Mode):")
print("Crowd")
for i, state in enumerate(result_crowd6.state_names['Crowding Risk']):
    print(f"    {state}: {result_crowd6.values[i]:.4f}")





print('\n')


# Inference 7
result_crowd7 = inference.query(variables=['Crowding Risk'], evidence={'Weather': 'Heavy','Day Type':'Weekday','Service Status':'Reduced','Network Mode':'Future'})
# Print predictions for each node
print("Given a Rainy Weekday with Disrupted Service (Future Mode):")
print("Crowd")
for i, state in enumerate(result_crowd7.state_names['Crowding Risk']):
    print(f"    {state}: {result_crowd7.values[i]:.4f}")
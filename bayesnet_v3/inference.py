from model import model
from pgmpy.inference import VariableElimination

# Create inference object
inference = VariableElimination(model)

# Calculate predictions given Crowding Risk is High
result_demand = inference.query(variables=['Demand Proxy'], evidence={'Crowding Risk': 'High'})
result_service = inference.query(variables=['Service Status'], evidence={'Crowding Risk': 'High'})
result_network = inference.query(variables=['Network Mode'], evidence={'Crowding Risk': 'High'})
result_day_type = inference.query(variables=['Day Type'], evidence={'Crowding Risk': 'High'})
result_weather = inference.query(variables=['Weather'], evidence={'Crowding Risk': 'High'})

# Print predictions for each node
print("Given Crowding Risk is High:")
print("\nDemand Proxy")
for i, state in enumerate(result_demand.state_names['Demand Proxy']):
    print(f"    {state}: {result_demand.values[i]:.4f}")

print("\nService Status")
for i, state in enumerate(result_service.state_names['Service Status']):
    print(f"    {state}: {result_service.values[i]:.4f}")

print("\nNetwork Mode")
for i, state in enumerate(result_network.state_names['Network Mode']):
    print(f"    {state}: {result_network.values[i]:.4f}")

print("\nDay Type")
for i, state in enumerate(result_day_type.state_names['Day Type']):
    print(f"    {state}: {result_day_type.values[i]:.4f}")

print("\nWeather")
for i, state in enumerate(result_weather.state_names['Weather']):
    print(f"    {state}: {result_weather.values[i]:.4f}")

print("\nCrowding Risk: High (given)")
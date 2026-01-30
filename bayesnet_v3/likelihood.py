from model import model
from pgmpy.inference import VariableElimination



evidence1 = {
    'Day Type': 'Weekday',
    'Weather': 'None',
    'Demand Proxy': 'Medium',
    'Service Status': 'Normal',
    'Network Mode': 'Today',
    'Crowding Risk': 'High'
}

# Find the probability of this specific state
probability = model.get_state_probability(evidence1)
print(f"Probability of Low Crowd on a Clear Weekday + Medium Demand + Normal Service \nToday Mode = {probability:.8f}")

evidence2 = {
    'Day Type': 'Weekday',
    'Weather': 'None',
    'Demand Proxy': 'Medium',
    'Service Status': 'Normal',
    'Network Mode': 'Future',
    'Crowding Risk': 'High'
}

# Find the probability of this specific state
probability = model.get_state_probability(evidence2)
print(f"Future Mode = {probability:.8f}")



print('\n\n')



evidence3 = {
    'Day Type': 'Weekend',
    'Weather': 'None',
    'Demand Proxy': 'Low',
    'Service Status': 'Normal',
    'Network Mode': 'Today',
    'Crowding Risk': 'Low'
}

# Find the probability of this specific state
probability = model.get_state_probability(evidence3)
print(f"Probability of Low Crowd on a Clear Weekday + Medium Demand + Normal Service \nToday Mode = {probability:.8f}")

evidence4 = {
    'Day Type': 'Weekend',
    'Weather': 'None',
    'Demand Proxy': 'Low',
    'Service Status': 'Normal',
    'Network Mode': 'Future',
    'Crowding Risk': 'Low'
}

# Find the probability of this specific state
probability = model.get_state_probability(evidence4)
print(f"Future Mode = {probability:.8f}")

print('\n\n')

evidence5 = {
    'Day Type': 'Weekday',
    'Weather': 'Heavy',
    'Demand Proxy': 'High',
    'Service Status': 'Disrupted',
    'Network Mode': 'Today',
    'Crowding Risk': 'High'
}

# Find the probability of this specific state
probability = model.get_state_probability(evidence5)
print(f"Probability of Low Crowd on a Clear Weekday + Medium Demand + Normal Service \nToday Mode = {probability:.8f}")

evidence6 = {
    'Day Type': 'Weekday',
    'Weather': 'Heavy',
    'Demand Proxy': 'High',
    'Service Status': 'Disrupted',
    'Network Mode': 'Future',
    'Crowding Risk': 'High'
}

# Find the probability of this specific state
probability = model.get_state_probability(evidence6)
print(f"Future Mode = {probability:.8f}")

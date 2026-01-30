from model import model
from pgmpy.inference import VariableElimination


# Calculate probability for a given observation
# P(Day Type=Weekday,Weather=None,Demand Proxy=Medium,Service Status=Normal,Network Mode=Today,Crowding Risk=Low)
evidence = {
    'Day Type': 'Weekday',
    'Weather': 'None',
    'Demand Proxy': 'Medium',
    'Service Status': 'Normal',
    'Network Mode': 'Today',
    'Crowding Risk': 'Low'
}

# Find the probability of this specific state
probability = model.get_state_probability(evidence)
print(f"P(Day Type=Weekday, Weather=None, Demand Proxy=Medium, Service Status=Normal, Network Mode=Today, Crowding Risk=Low) = {probability:.6f}")
print(f"= {probability:.8f}")
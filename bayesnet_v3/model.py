from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD

# Create a Bayesian Network structure
model = BayesianNetwork([
    ('Day Type', 'Demand Proxy'),
    ('Weather', 'Demand Proxy'),
    ('Demand Proxy', 'Crowding Risk'),
    ('Service Status', 'Crowding Risk'),
    ('Network Mode', 'Crowding Risk')
])

# Day Type CPD (no parents)
cpd_day_type = TabularCPD(
    variable='Day Type', 
    variable_card=2,
    values=[[0.7], [0.3]],  # Weekday | Weekend
    state_names={'Day Type': ['Weekday', 'Weekend']}
)

# Weather CPD (no parents)
cpd_weather = TabularCPD(
    variable='Weather', 
    variable_card=4,
    values=[
        [0.33333],    # None
        [0.333335],   # Light
        [0.066667],   # Moderate
        [0.266668]    # Heavy
    ],
    state_names={'Weather': ['None', 'Light', 'Moderate', 'Heavy']}
)

# Demand Proxy CPD (conditional on Day Type and Weather)
# We need to create reasonable conditional probabilities based on your description
# Let's assume that Weekdays and bad weather increase demand
cpd_demand = TabularCPD(
    variable='Demand Proxy',
    variable_card=3,
    values=[
        # Order: Weather=None, Light, Moderate, Heavy for both Day Types
        # Low demand probabilities
        [0.4, 0.3, 0.2, 0.1, 0.6, 0.5, 0.4, 0.3],
        # Medium demand probabilities  
        [0.3, 0.4, 0.3, 0.2, 0.2, 0.3, 0.3, 0.2],
        # High demand probabilities
        [0.3, 0.3, 0.5, 0.7, 0.2, 0.2, 0.3, 0.5]
    ],
    evidence=['Day Type', 'Weather'],
    evidence_card=[2, 4],
    state_names={
        'Demand Proxy': ['Low', 'Medium', 'High'],
        'Day Type': ['Weekday', 'Weekend'],
        'Weather': ['None', 'Light', 'Moderate', 'Heavy']
    }
)

# Service Status CPD (no parents)
cpd_service = TabularCPD(
    variable='Service Status',
    variable_card=3,
    values=[
        [0.999],      # Normal
        [0.024623],  # Reduced
        [0.075377]   # Disrupted
    ],
    state_names={'Service Status': ['Normal', 'Reduced', 'Disrupted']}
)

# Network Mode CPD (no parents)
cpd_network = TabularCPD(
    variable='Network Mode',
    variable_card=2,
    values=[[0.57447], [0.42553]],  # Today, Future
    state_names={'Network Mode': ['Today', 'Future']}
)

# Crowding Risk CPD (conditional on Demand Proxy, Service Status, and Network Mode)
cpd_crowding = TabularCPD(
    variable='Crowding Risk',
    variable_card=3,
    values=[
        # Low crowding (Demand:6, Service:2, Mode:1)
        [0.8, 0.85, 0.7, 0.75, 0.6, 0.65, 0.5, 0.55, 0.4, 0.45, 0.3, 0.35, 0.2, 0.25, 0.1, 0.15, 0, 0.05],  # Low Demand Today / Future
         
        # Medium crowding (Demand:6, Service:2, Mode:1)
        [0.1, 0.07, 0.1, 0.13, 0.08, 0.07, 0.09, 0.11, 0.1, 0.07, 0.03, 0.06,0.08, 0.07,  0.1, 0.11, 0.05, 0.13], # Today / Future
         
        # High crowding (Demand:6, Service:2, Mode:1)
        [0.1, 0.08, 0.2, 0.12, 0.32, 0.28, 0.41, 0.34, 0.5, 0.48, 0.67, 0.59, 0.72, 0.68, 0.8, 0.74, 0.95, 0.82]   # Today / Future
    ],
    evidence=['Demand Proxy', 'Service Status', 'Network Mode'],
    evidence_card=[3, 3, 2],
    state_names={
        'Crowding Risk': ['Low', 'Medium', 'High'],
        'Demand Proxy': ['Low', 'Medium', 'High'],
        'Service Status': ['Normal', 'Reduced', 'Disrupted'],
        'Network Mode': ['Today', 'Future']
    }
)

# Add CPDs to the model
model.add_cpds(cpd_day_type, cpd_weather, cpd_demand, 
               cpd_service, cpd_network, cpd_crowding)

# Verify model
assert model.check_model()
from collections import Counter
from model import model
from pgmpy.sampling import BayesianModelSampling

# Create sampling object
sampler = BayesianModelSampling(model)

# Rejection sampling
# Compute distribution of Appointment given that train is delayed
N = 10000
data = []

# Generate samples
samples = sampler.forward_sample(size=N)

# Filter samples where train is delayed
for _, row in samples.iterrows():
    if row['train'] == 'delayed':
        data.append(row['appointment'])

print(f"Samples where train is delayed: {len(data)}")
print(Counter(data))


# Bayesian Network Docker Setup

This project runs a Bayesian Network for train scheduling inference using Docker Compose.

## Files

- `model.py` - Defines the Bayesian Network structure and probability distributions
- `inference.py` - Performs inference to calculate probabilities given evidence
- `sample.py` - Uses rejection sampling to estimate probabilities
- `Dockerfile` - Docker image configuration
- `docker-compose.yml` - Docker Compose orchestration
- `requirements.txt` - Python dependencies (pgmpy, pandas)

## Running the Application

## Run this
pip install -r bayesnet_v3/requirements.txt

### Run inference (default):
python bayesnet_v3/inference.py

## Output

**Inference output** shows the probability of crowding risks.

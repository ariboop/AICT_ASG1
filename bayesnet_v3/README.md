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

### Run inference (default):
```bash
docker-compose up
```

### Run sampling:
Edit `docker-compose.yml` and uncomment the `command: python sample.py` line, then:
```bash
docker-compose up
```

### Rebuild after code changes:
```bash
docker-compose up --build
```

### Stop and remove containers:
```bash
docker-compose down
```

## Output

**Inference output** shows the probability distribution of rain, maintenance, and appointment given that the train is delayed.

**Sampling output** uses Monte Carlo rejection sampling to estimate the appointment attendance distribution when the train is delayed.

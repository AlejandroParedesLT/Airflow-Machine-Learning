# Project Overview

This project implements a batch processing pipeline using Apache Airflow and provides a Django backend with two key services: a Default Credit Scoring system (processed asynchronously in the background) and a Sentiment Analysis service based on a BERT model. 

These services are designed for scalability, with the ability to handle large data volumes efficiently and ensure accurate model-driven decisions.

# Project Structure
```bash
dags/
    ├── prediction_CreditRiskScoring.py
    └── prediction_NLPSentiment.py
django_api/
    ├── api/  # The implementation of the services for CreditRiskScoring and NLPSentiment
    │   ├── components/  # Classes for the models
    │   ├── database/  # Management of queries to the database
    │   └── models/  # Pretrained models
    └── model_deploy/  # URL routing and endpoints
```

# Project components:

### Apache Airflow

Apache Airflow is used to orchestrate and manage batch processing workflows. It enables the deployment of machine learning cycles and ETLs in a scalable, replicable way. Airflow provides a powerful platform for monitoring, scheduling, and executing workflows, with Python support for seamless integration into data engineering pipelines.

![Dashboard_Overview](Dashboard.JPG)

![Dag_Overview](DAG.JPG)

## Usage of Apache Airflow in the context of this project
Airflow uses DAGs (Directed Acyclic Graph) which are scripts that can be programmed to run in a controlled schedule. It provides features like retries in case the proces fails and also has a mailing service to be used as a error fail notification.  

For the implementation of the services of this project we have two specific DAGs

- **prediction_CreditRiskScoring**: Sends a post request with no payload that triggers a batch process to calculate the score retrieving data from SQL Server, batch processing.
- **prediction_NLPSentiment**: Loops over a set of strings and for each string sends a post request with the string as payload, it gets as a response the classification class of the string from the NLP Hugging Face model deployed in the backend of Django

## Usage of Django in this project

The Django framework is used to implement two services: the Default Credit Scoring system and the Sentiment Analysis service. These services are exposed through API endpoints, enabling users to interact with the models efficiently.

### Key Components:

1. **API Implementation (`django_api/api`)**:
    - This folder contains the core logic for both the Credit Scoring and Sentiment Analysis services. It acts as the interface between the backend models and the external requests.
    - The API receives requests, processes data through the respective models, and returns results to the user.

2. **Components (`django_api/api/components`)**:
    - This directory houses the essential classes and utilities that support model operations. It contains the code that interacts with the models and performs necessary transformations on the input data.

3. **Database Management (`django_api/api/database`)**:
    - This module handles the interaction with the database, including querying and storing data needed by the application. It ensures that the required data is available for the models to process and provides a structured way to manage database operations.

4. **Pretrained Models (`django_api/api/models`)**:
    - This folder contains the pretrained machine learning models used for both the Default Credit Scoring system and the Sentiment Analysis service. These models are loaded when the application starts and are used to generate predictions for incoming requests.

5. **Model Deployment and Routing (`django_api/model_deploy`)**:
    - This section manages the URL routing and API endpoints. It defines how requests are mapped to the underlying services, allowing users to submit credit scoring tasks or text for sentiment analysis through well-defined endpoints.
    - The routing logic ensures that requests are handled asynchronously when necessary (for example, the credit scoring task is processed in the background).

### Asynchronous Processing:

The Default Credit Scoring service leverages Django's integration with Celery to process tasks asynchronously. This ensures that larger tasks, such as scoring credit risk for multiple clients, are offloaded to background workers and do not block the main application.

### Real-Time Sentiment Analysis:

The Sentiment Analysis service is designed to provide real-time feedback to the user. Once text input is submitted via the API, it is immediately passed through the BERT-based model to return a sentiment classification.

In summary, Django is used to manage API interactions, handle background processing, and serve machine learning models in a scalable, structured way within the current context.


## Software Tools

- Python
- PySpark
- Apache Airflow
- Machine Learning and Deep Learning Dependencies

## How to Run the project?

1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```

## Airflow build procedure

2. Build the Docker image:
    ```bash
    docker build -f Dockerfile -t 'extending_airflow:latest' .
    ```

3. Start the Airflow environment:
    ```bash
    docker-compose up
    ```

## Django Build

1. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Run the Django development server**:
    ```bash
    python manage.py runserver
    ```
---

This project is built to handle scalable, production-ready batch processing and real-time machine learning predictions using Airflow for orchestration and Django for API management.

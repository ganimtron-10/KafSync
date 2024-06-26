#!/bin/bash

# Step 1: Set up Kafka using Docker Compose
docker-compose -f app/kafka/compose.yaml up -d

# Step 2: Install Required Python Libraries
pip install -r requirements.txt

# Step 3: Create a .env File
# Replace the placeholders with your actual values
echo 'SQLALCHEMY_DATABASE_URL=<Your SQLAlchemy Database URL>' > .env
echo 'STRIPE_API_KEY=<Your Stripe API key>' >> .env

# Step 4: Execute Kafka Resources Setup
python -m app.kafka.admin.py

# Step 5: Start the Server
uvicorn app.main:app --reload &

# Step 6: Choose Between Polling or Webhook Setup
### Option 1: Polling
### Start the Scheduled Poller
python -m app.schedule-poll.py &

### Option 2: Webhook Setup
### Manually set up a webhook endpoint in your local environment. I am using localtunnel for exposing the local server to the internet.
lt -p 8000
### Note the generated public URL, then go to your Stripe account and configure the webhook endpoint 
### Webhook Endpoint URL would look like https://{public_URL}/api/v1/customers/webhook


# Step 7: Start the Kafka Consumer
python -m app.kafka.consumer.py &

echo "KafSync is now running. Access the API at http://localhost:8000/docs."

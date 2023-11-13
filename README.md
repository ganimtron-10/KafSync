# KafSync

Kafsync is a simple integration application that synchronizes customer data between your local environment and Stripe, a popular payment processing platform. It leverages Kafka as a messaging system to facilitate real-time data synchronization.

## Local Setup

Follow these steps to set up Kafsync locally:

1. **Setup Kafka Using Docker:**

   - Use the provided Docker Compose file at `app/kafka/compose.yaml` to set up a Kafka instance locally. Make sure you have Docker installed.
   - Run the following command to start Kafka:
     ```
     docker-compose -f app/kafka/compose.yaml up
     ```

2. **Install Required Libraries:**

   - Install the required Python libraries by running:
     ```
     pip install -r requirements.txt
     ```

3. **Create a .env File:**

   - Create a `.env` file in the project root directory to store sensitive information such as URLs and API keys.
   - Configure the following environment variables in the `.env` file:

     ```
     SQLALCHEMY_DATABASE_URL=<Your SQLAlchemy Database URL>
     STRIPE_API_KEY=<Your Stripe API key>
     ```

4. **Execute Kafka Resources Setup:**

   - Run `app/kafka/admin.py` to configure Kafka resources, including topics and partitions.

5. **Choose Between Polling or Webhook Setup:**

   - Decide on the synchronization method for Stripe integration. You can either use the polling mechanism or set up a webhook endpoint in Stripe.
  
      - **Option 1: Polling Mechanism**
        Start the scheduled poller by running the following command:
        ```bash
        python -m app.schedule-poll.py
        ```
  
      - **Option 2: Webhook Setup**
        Manually set up a webhook endpoint in your local environment using a tool like Ngrok or Localtunnel. Note the public URL generated and configure it in your Stripe account like https://{public_URL}/api/v1/customers/webhook. LocalTunnel usage can be as follows:
        ```bash
        npm install -g localtunnel
        lt -p 8000
        ```

6. **Start the Server:**

   - Run the following command to start the server using Uvicorn with auto-reload:
     ```
     uvicorn app.main:app --reload
     ```

7. **Execute Kafka Consumer:**

   - Start the Kafka consumer by running `app/kafka/consumer.py`. This consumer listens for events and processes data for synchronization.

8. **Access the API:**

   - Open a web browser and navigate to `http://localhost:8000/docs` to interact with the API endpoints. Use this interface to trigger events for customer synchronization.

9. **Interact with Stripe:**

   - Access your Stripe account and interact with it to observe the two-way synchronization between your local environment and Stripe.

You should now be able to see the synchronization in action.

## Usage

- Use the provided API documentation (Swagger) at `http://localhost:8000/docs` to create, update, and delete customer records. These changes will be propagated to Stripe and vice versa in near real-time.

## Next Steps


Checkout [Issues](https://github.com/ganimtron-10/KafSync/issues) section for more information on things that are to be implemented, improved, and fixed.



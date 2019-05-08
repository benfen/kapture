# Kafka Messenger

This app serves as a quick go-between anything that can dispatch HTTP requests and a Kafka instance.  It exposes a single GET endpoint that takes data as part of the URL and then forwards that to Kafka.

Alternatively, it allows for subscribing to Kafka and sending those messages to Redis to store.  The application will only do one of these at a time, based on the configuration flags that are passed into the application.

This server expects data to conform to the structure of Apache's BigPetStore.  If the incoming data is not a superset of the structure of the BigPetStore data, the server will error out.

# Usage

The app can be compiled using gradle.  Run `gradle build` to generate a runnable jar of the application.  Alternatively, one can run `build-image.sh` inside of the `scripts` directory located adjacent to this directory.  That will invoke a gradle build and attempt to publish the resulting image into DockerHub.

The app is also available in the form of a docker container - `docker run -it benfen/dummy-kafka-messenger:latest`

## Configuration

For configuration, the app will look at environment variables to determine what to do at runtime:
* `BROKERS` - This variable should contain the comma-separated list of Kafka brokers for the server to dispatch messages to.
* `GROUP_ID` - Used by the listener.  Identifies the consumer to Kafka.
* `MESSENGER_MODE` - Indicates whether the server should be listening for messages from Kafka to send to Redis or listen for messages to send to Kafka.  If the value is 'REDIS_LISTEN' it will it will listen to messages from Kafka and send them to Redis.  If no value is provided or the value is an empty string, it will function as a load generator.  Note that invalid values - values that are defined but neither 'REDIS_LISTEN' nor 'ELASTIC-LISTEN' - will cause the messenger to error out.
* `REDIS_HOST` - Used by the listener.  The IP (or DNS name) of the redis server.  This is used to send messages from Kafka to Redis.
* `STORE_COUNT` - Used by the producer.  Indicates the number of stores.

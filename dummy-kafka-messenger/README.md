# Kafka Messenger

This app serves as a quick go-between anything that can dispatch HTTP requests and a Kafka instance.  It exposes a single GET endpoint that takes data as part of the URL and then forwards that to Kafka.

Alternatively, it allows for subscribing to Kafka and sending those messages to Redis to store.  The application will only do one of these at a time, based on the configuration flags that are passed into the application.

This server expects data to conform to the structure of Apache's BigPetStore.  If the incoming data does not do this, the server will error out.

# Usage

The app can be compiled using gradle.  Run `gradle build` to generate a runnable jar of the application.  Alternatively, one can run `build-image.sh` inside of the `scripts` directory located adjacent to this directory.  That will invoke a gradle build and attempt to publish the resulting image into DockerHub.

The app is also available in the form of a docker container - `docker run -it benfen/dummy-kafka-messenger:latest`

## Configuration

For configuration, the app will look at environment variables to determine what to do at runtime:
* `BROKERS` - This variable should contain the list of Kafka brokers for the server to dispatch messages to.
* `GROUP_ID` - Used by the listener.  Identifies the consumer to Kafka.
* `MESSENGER_MODE` - Indicates whether the server should be listening for messages from Kafka to send to Redis or listen for messages to send to Kafka.  If the value is 'listen', then it will consume messages from Kafka; otherwise it will produce them and send them into Kafka.
* `REDIS_HOST` - Used by the listener.  The IP (or DNS name) of the redis server.  This is used to send messages from Kafka to Redis.
* `STORE_COUNT` - Used by the listener.  Should indicate the number of stores (i.e. the number of Kafka topics).  This is used to create a consumer listening to all of those topics.

If any of these variables are not defined, the app will refuse to start.

# Kafka Messenger

This app serves as a quick go-between anything that can dispatch HTTP requests and a Kafka instance.  It exposes a single GET endpoint that takes data as part of the URL and then forwards that to Kafka.

This server expects data to conform to the structure of Apache's BigPetStore.  If the incoming data does not do this, the server will error out.

# Usage

The app can be compiled using gradle.  Run `gradle build` to generate a runnable jar of the application.

The app is also available in the form of a docker container - `docker run -it benfen/dummy-kafka-messenger:latest`

## Configuration

For configuration, the app will look at environment variables to determine what to do at runtime:
* `BROKERS` - This variable should contain the list of Kafka brokers for the server to dispatch messages to.

If either or both of these variables are not defined, the app will refuse to start.

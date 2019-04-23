enum class MessengerMode {
    /**
     * Indicate that the program should listen to Kafka and dispatch the information into elastic search
     */
    ELASTIC_LISTEN,

    /**
     * Indicate that the program should listen to Kafka and dispatch the information to Redis
     */
    REDIS_LISTEN,
}
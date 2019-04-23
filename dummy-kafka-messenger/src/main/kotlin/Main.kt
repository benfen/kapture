import io.prometheus.client.exporter.HTTPServer

private val messengerMode = System.getenv("MESSENGER_MODE")

fun main() {
    // Start the prometheus server
    val server = HTTPServer("0.0.0.0", 7001)

    if (messengerMode == null || messengerMode.isEmpty()) {
        startProducer()
    } else {
        val mode = MessengerMode.valueOf(messengerMode)

        try {
            startListener(mode)
        } finally {
            // The Prometheus server will keep the JAR running even if it fails, so it needs to be explicitly stopped on error
            server.stop()
        }
    }
}
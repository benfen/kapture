import io.prometheus.client.exporter.HTTPServer

private val messengerMode: String? = System.getenv("MESSENGER_MODE")

fun main() {
    if (messengerMode != null && messengerMode.toLowerCase() == "listen") {
        // Start the prometheus server
        val server = HTTPServer(7001)

        try {
            startConsumer()
        } finally {
            // The Prometheus server will keep the JAR running even if it fails, so it needs to be explicitly stopped on error
            server.stop()
        }

    } else {
        startProducer()
    }
}
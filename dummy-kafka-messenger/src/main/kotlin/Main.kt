import io.prometheus.client.exporter.HTTPServer

private val messengerMode = System.getenv("MESSENGER_MODE")

fun main() {
    // Start the prometheus server
    val server = HTTPServer("0.0.0.0", 7001)

    try {
        if (messengerMode == null || messengerMode.isEmpty()) {
            startProducer()
        } else {
            val mode = MessengerMode.valueOf(messengerMode)

            startListener(mode)
        }
    } catch (e: Exception) {
        server.stop()
        throw e
    }
}
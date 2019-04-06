private val messengerMode: String? = System.getenv("MESSENGER_MODE")

fun main() {
    if (messengerMode != null && messengerMode.toLowerCase() == "listen") {
        startConsumer()
    } else {
        startProducer()
    }
}
import io.javalin.Javalin
import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.Producer
import org.apache.kafka.clients.producer.ProducerRecord
import org.apache.kafka.common.serialization.StringSerializer
import org.slf4j.LoggerFactory
import java.util.Properties
import kotlinx.serialization.json.Json

private val brokerList: String? = System.getenv("BROKERS")

private fun createProducer(brokers: String): Producer<String, String> {
    val props = Properties()
    props["bootstrap.servers"] = brokers
    props["key.serializer"] = StringSerializer::class.java.canonicalName
    props["value.serializer"] = StringSerializer::class.java.canonicalName
    return KafkaProducer<String, String>(props)
}

fun startProducer() {
    val logger = LoggerFactory.getLogger("server")

    if (brokerList == null) {
        logger.error("Environment variable 'BROKERS' must be defined")
        System.exit(1)
    } else {
        logger.info("Brokers: {}", brokerList)
        val app = Javalin.create().start(7000)

        val producer = createProducer(brokerList)
        app.get("/:message") { ctx ->
            val message = ctx.pathParam("message")

            val data = Json.parse(PetStoreTransaction.serializer(), message)
            val topic = data.store.location.state

            producer.send(ProducerRecord(topic, data.dateTime.toString(), message)).get()
        }
    }
}
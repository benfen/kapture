import io.javalin.Javalin
import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.Producer
import org.apache.kafka.clients.producer.ProducerRecord
import org.apache.kafka.common.serialization.StringSerializer
import org.slf4j.LoggerFactory
import java.util.Properties

val brokerList: String? = System.getenv("BROKERS")
val topic: String? = System.getenv("TOPIC")

fun createProducer(brokers: String): Producer<String, String> {
    val props = Properties()
    props["bootstrap.servers"] = brokers
    props["key.serializer"] = StringSerializer::class.java.canonicalName
    props["value.serializer"] = StringSerializer::class.java.canonicalName
    return KafkaProducer<String, String>(props)
}

fun main(args: Array<String>) {
    val logger = LoggerFactory.getLogger("server")

    if (brokerList == null || topic == null) {
        logger.error("Environment variables 'brokers' and 'topic' must be defined")
        System.exit(1)
    } else {
        logger.info("Brokers: {} , Topic: {}", brokerList, topic)
        val app = Javalin.create().start(7000)

        val producer = createProducer(brokerList)
        app.get("/:message") { ctx -> producer.send(ProducerRecord(topic, ctx.pathParam("message"))).get() }
    }
}
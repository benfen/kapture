import io.prometheus.client.Counter
import io.prometheus.client.exporter.HTTPServer
import org.apache.kafka.clients.consumer.Consumer
import org.apache.kafka.clients.consumer.ConsumerRecords
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.common.serialization.StringDeserializer
import org.slf4j.LoggerFactory
import redis.clients.jedis.Jedis
import java.util.Properties

private val brokerList: String? = System.getenv("BROKERS")
private val groupId: String? = System.getenv("GROUP_ID")
private val redisHost: String? = System.getenv("REDIS_HOST")
private val stores: String? = System.getenv("STORE_COUNT")

private fun createConsumer(brokers: String, groupId: String): Consumer<String, String> {
    val props = Properties()
    props["bootstrap.servers"] = brokers
    props["group.id"] = groupId
    props["key.deserializer"] = StringDeserializer::class.java.canonicalName
    props["value.deserializer"] = StringDeserializer::class.java.canonicalName
    return KafkaConsumer<String, String>(props)
}

fun startConsumer() {

    val logger = LoggerFactory.getLogger("server")

    if (brokerList == null || groupId == null || redisHost == null || stores == null) {
        logger.error("Environment variables 'BROKERS', 'GROUP_ID', 'REDIS_HOST', and 'STORE_COUNT' must be defined")
        System.exit(1)
    } else {
        // Start the prometheus server
        HTTPServer(7001)

        val counter = Counter.build()
                .name("kafka_transactions")
                .help("Total number of kafka transactions seen by this node")
                .register()

        val storeCount = Integer.parseInt(stores)

        val topics = ArrayList<String>()
        for (i in 0..storeCount) {
            topics.add("Store_$i")
        }

        val consumer = createConsumer(brokerList, groupId)
        consumer.subscribe(topics)

        val jedis = Jedis(redisHost)
        while (true) {
            val records: ConsumerRecords<String, String> = consumer.poll(100)

            for (record in records) {
                jedis.set(record.key(), record.value())
            }

            counter.inc(records.count().toDouble())
        }
    }

}
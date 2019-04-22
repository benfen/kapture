import com.mashape.unirest.http.Unirest
import io.prometheus.client.Counter
import org.apache.kafka.clients.consumer.Consumer
import org.apache.kafka.clients.consumer.ConsumerRecord
import org.apache.kafka.clients.consumer.ConsumerRecords
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.common.serialization.StringDeserializer
import org.redisson.Redisson
import org.redisson.config.Config
import org.slf4j.LoggerFactory
import java.util.Properties

private val brokerList: String? = System.getenv("BROKERS")
private val elasticHost: String? = System.getenv("ELASTIC_HOST")
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

fun startListener(mode: MessengerMode) {

    val logger = LoggerFactory.getLogger("server")
    val dispatch: (record: ConsumerRecord<String, String>) -> Any

    when(mode) {
        MessengerMode.ELASTIC_LISTEN -> {
            if (elasticHost == null) {
                logger.error("Environment variable 'ELASTIC_HOST' must be defined when the message mode is 'ELASTIC_LISTEN")
                System.exit(1)
            }

            dispatch = { record -> Unirest.post("$elasticHost/${record.topic()}/store")
                    .header("Content-Type", "application/json")
                    .body(record.value())
                    .asStringAsync() }
        }
        MessengerMode.REDIS_LISTEN -> {
            if (redisHost == null) {
                logger.error("Environment variable 'REDIS_HOST' must be defined when the message mode is 'REDIS_LISTEN")
                System.exit(1)
            }

            val config = Config()
            config.useSentinelServers()
                    .setMasterName("mymaster")
                    .addSentinelAddress("redis://$redisHost")
            val client = Redisson.create(config)

            dispatch = { record -> client.getBucket<String>(record.key()).setAsync(record.value()).get() }
        }
    }

    if (brokerList == null || groupId == null || stores == null) {
        logger.error("Environment variables 'BROKERS', 'GROUP_ID', and 'STORE_COUNT' must be defined")
        System.exit(1)
    } else {

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

        while (true) {
            val records: ConsumerRecords<String, String> = consumer.poll(100)

            for (record in records) {
                dispatch(record)
            }

            counter.inc(records.count().toDouble())
        }
    }

}
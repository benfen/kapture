FROM anapsix/alpine-java:latest

ADD ./scripts/fetch-deps.sh /opt
RUN /opt/fetch-deps.sh

ADD ./scripts/redis-kafka-connector.sh /opt
ADD ./dummy-kafka-messenger/build/libs/dummy-kafka-messenger-1.0-SNAPSHOT.jar /opt

ENV TOPIC ""
ENV BROKERS ""

ENV KAFKA_URL ""
ENV REDIS_URL ""
ENV ZOOKEEPER_URL ""

CMD java -jar /opt/dummy-kafka-messenger-1.0-SNAPSHOT.jar

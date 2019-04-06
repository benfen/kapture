FROM anapsix/alpine-java:latest

ADD ./scripts/fetch-deps.sh /opt
RUN /opt/fetch-deps.sh

ADD ./scripts/generate-topics.sh /opt
ADD ./dummy-kafka-messenger/build/libs/dummy-kafka-messenger-1.0-SNAPSHOT.jar /opt

CMD java -jar /opt/dummy-kafka-messenger-1.0-SNAPSHOT.jar

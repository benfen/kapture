FROM anapsix/alpine-java:latest

ADD ./build/libs/dummy-kafka-messenger-1.0-SNAPSHOT.jar /opt
ENV TOPIC ""
ENV BROKERS ""

CMD java -jar /opt/dummy-kafka-messenger-1.0-SNAPSHOT.jar

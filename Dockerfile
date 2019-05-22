FROM gcr.io/google_samples/k8skafka:v1

RUN apt-get update -y
RUN apt-get install inotify-tools python3 python3-pip redis-server redis-sentinel -y
RUN pip3 install prometheus_client psycopg2-binary

ADD ./scripts/container/dispatch-messages.sh /opt
ADD ./scripts/container/generate-topics.sh /opt
ADD ./scripts/container/redis-connector.sh /opt
ADD ./scripts/container/kafka-metrics.py /opt
ADD ./scripts/container/postgres-connector.py /opt
ADD ./scripts/container/postgres-connector.sh /opt

WORKDIR /opt

CMD [ "sleep", "1" ]

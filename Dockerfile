FROM gcr.io/google_samples/k8skafka:v1

RUN apt-get update -y
RUN apt-get install inotify-tools python3 python3-pip redis-server redis-sentinel -y
RUN pip3 install prometheus_client psycopg2

ADD ./scripts/dispatch-messages.sh /opt
ADD ./scripts/generate-topics.sh /opt
ADD ./scripts/redis-connector.sh /opt
ADD ./scripts/kafka-metrics.py /opt
ADD ./scripts/postgres-connector.py /opt

WORKDIR /opt

CMD [ "sleep", "1" ]

FROM gcr.io/google_samples/k8skafka:v1

ADD ./scripts/fetch-deps.sh /opt
RUN /opt/fetch-deps.sh

ADD ./scripts/dispatch-messages.sh /opt
ADD ./scripts/generate-topics.sh /opt
ADD ./scripts/redis-connector.sh /opt
ADD ./scripts/kafka-metrics.py /opt

WORKDIR /opt

CMD [ "sleep", "1000" ]

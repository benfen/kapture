FROM anapsix/alpine-java:latest

ADD ./scripts/fetch-deps.sh /opt
RUN /opt/fetch-deps.sh

ADD ./scripts/dispatch-messages.sh /opt
ADD ./scripts/generate-topics.sh /opt
ADD ./scripts/redis-connector.sh /opt

WORKDIR /opt

CMD [ "sleep", "1000" ]

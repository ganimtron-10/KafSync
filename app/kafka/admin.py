from confluent_kafka.admin import AdminClient, NewTopic

admin_client = AdminClient({'bootstrap.servers': 'localhost'})

new_topics = [NewTopic(topic, num_partitions=3, replication_factor=1)
              for topic in ["stripe"]]

fs = admin_client.create_topics(new_topics)

for topic, f in fs.items():
    try:
        f.result()
        print("Topic {} created".format(topic))
    except Exception as e:
        print("Failed to create topic {}: {}".format(topic, e))

#! /usr/bin/env bash

start_kafka () {
	python3.10 manage.py kafka_gcn > >(tee -a logs/kafka_stdout.log) 2> >(tee -a logs/kafka_stderr.log >&2)
	return 1
	#return $?
}



until start_kafka; do
	echo "Kafka died with exit code $?, restarting..." >> logs/kafka_sterr.log
	sleep 1
done

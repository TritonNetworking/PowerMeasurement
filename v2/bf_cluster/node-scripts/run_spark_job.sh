SRC_DIR_FULL_PATH=$1
RESULTS_DIR_FULL_PATH=$2
SIZE_IN_MB=$3
SCALA_CLASS_NAME=$4

# Needed when running from sshclient in Python
# export JAVA_HOME=/usr/lib/jvm/java-8-oracle; 

# Run spark job
spark-submit --class PowerMeasurements.${SCALA_CLASS_NAME} \
        --num-executors 40 --executor-cores 5 --executor-memory 10g --driver-cores 5 --driver-memory 5g \
        "${SRC_DIR_FULL_PATH}/target/scala-2.11/sparksort_2.11-0.1.jar" \
        yarn "/user/ayelam/sort_inputs/${SIZE_IN_MB}mb.input" "/user/ayelam/sort_outputs/${SIZE_IN_MB}mb.output" \
        "/user/ayelam/sort_stats/${SIZE_IN_MB}mb.stats" > ${RESULTS_DIR_FULL_PATH}/spark.log 2>&1

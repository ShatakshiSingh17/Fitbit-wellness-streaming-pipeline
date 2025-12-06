from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, to_date, to_timestamp, window, sum as _sum, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, LongType
import os

# Configuration - Use absolute paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAFKA_TOPIC = "fitbit_wellness_stream"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
BRONZE_PATH = os.path.join(PROJECT_ROOT, "data", "bronze", "daily_activity")
SILVER_PATH = os.path.join(PROJECT_ROOT, "data", "silver", "daily_activity")
GOLD_PATH = os.path.join(PROJECT_ROOT, "data", "gold", "daily_activity_kpi")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "data", "checkpoints")

def create_spark_session():
    return SparkSession.builder \
        .appName("FitbitWellnessETL") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0") \
        .getOrCreate()

def get_activity_schema():
    # Schema matching dailyActivity_merged.csv
    return StructType([
        StructField("Id", StringType(), True),
        StructField("ActivityDate", StringType(), True),
        StructField("TotalSteps", StringType(), True), # Read as string initially to handle potential bad data
        StructField("TotalDistance", StringType(), True),
        StructField("TrackerDistance", StringType(), True),
        StructField("LoggedActivitiesDistance", StringType(), True),
        StructField("VeryActiveDistance", StringType(), True),
        StructField("ModeratelyActiveDistance", StringType(), True),
        StructField("LightActiveDistance", StringType(), True),
        StructField("SedentaryActiveDistance", StringType(), True),
        StructField("VeryActiveMinutes", StringType(), True),
        StructField("FairlyActiveMinutes", StringType(), True),
        StructField("LightlyActiveMinutes", StringType(), True),
        StructField("SedentaryMinutes", StringType(), True),
        StructField("Calories", StringType(), True),
        StructField("ingestion_timestamp", StringType(), True)
    ])

def process_bronze(spark):
    """
    Reads from Kafka, writes raw events to Bronze (Parquet).
    """
    print("Starting Bronze Stream...")
    
    # Read from Kafka
    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON payload
    schema = get_activity_schema()
    df_parsed = df_kafka.select(
        from_json(col("value").cast("string"), schema).alias("data"),
        col("timestamp").alias("kafka_timestamp")
    ).select("data.*", "kafka_timestamp")

    # Write to Bronze
    query = df_parsed.writeStream \
        .format("parquet") \
        .option("path", BRONZE_PATH) \
        .option("checkpointLocation", f"{CHECKPOINT_PATH}/bronze") \
        .outputMode("append") \
        .start()
    
    return query

def process_silver(spark):
    """
    Reads from Bronze, cleans/validates, writes to Silver (Parquet).
    """
    print("Starting Silver Stream...")
    
    # Read from Bronze
    df_bronze = spark.readStream \
        .format("parquet") \
        .schema(spark.read.parquet(BRONZE_PATH).schema if spark.read.parquet(BRONZE_PATH).count() > 0 else get_activity_schema()) \
        .load(BRONZE_PATH) # Note: In real run, schema inference on streaming requires setting schema explicitly or enabling schema inference
    
    # If Bronze is empty initially, this might fail without explicit schema. 
    # For robustness in this script, we'll reuse the schema logic or assume Bronze is populated.
    # A better pattern for streaming from file source is specifying schema.
    
    # Transformations
    df_cleaned = df_bronze \
        .withColumn("TotalSteps", col("TotalSteps").cast(IntegerType())) \
        .withColumn("Calories", col("Calories").cast(DoubleType())) \
        .withColumn("ActivityDate", to_date(col("ActivityDate"), "M/d/yyyy")) \
        .withColumn("processing_timestamp", current_timestamp()) \
        .filter(col("TotalSteps") >= 0) \
        .filter(col("Calories") >= 0) \
        .dropDuplicates(["Id", "ActivityDate"])

    # Write to Silver
    query = df_cleaned.writeStream \
        .format("parquet") \
        .option("path", SILVER_PATH) \
        .option("checkpointLocation", f"{CHECKPOINT_PATH}/silver") \
        .outputMode("append") \
        .start()
    
    return query

def process_gold(spark):
    """
    Reads from Silver, aggregates KPIs by User AND Date, writes to Gold.
    """
    print("Starting Gold Stream...")
    
    # Read from Silver
    # We need the schema of Silver.
    schema_silver = StructType([
        StructField("Id", StringType(), True),
        StructField("ActivityDate", StringType(), True), # DateType in parquet
        StructField("TotalSteps", IntegerType(), True),
        StructField("Calories", DoubleType(), True),
        StructField("VeryActiveMinutes", IntegerType(), True),
        StructField("SedentaryMinutes", IntegerType(), True),
        # ... other fields
    ])
    
    df_silver = spark.readStream \
        .format("parquet") \
        .option("basePath", SILVER_PATH) \
        .schema(schema_silver) \
        .load(SILVER_PATH)

    # Aggregations: Daily Stats per User
    # Group by Id AND ActivityDate to preserve daily granularity for Tableau trends
    
    df_kpi = df_silver.groupBy("Id", "ActivityDate") \
        .agg(
            _sum("TotalSteps").alias("total_steps"),
            _sum("Calories").alias("total_calories"),
            _sum("VeryActiveMinutes").alias("very_active_minutes"),
            _sum("SedentaryMinutes").alias("sedentary_minutes")
        ) \
        .withColumn("wellness_score", 
                   (col("total_steps") / 10000 * 50) + 
                   ((1440 - col("sedentary_minutes")) / 480 * 50)
        ) # Simple mock wellness score calculation

    # Write to Gold (Complete mode for aggregations)
    # For Tableau, we might ideally want to write to CSV or Parquet, 
    # but 'complete' mode is tricky with file sinks in structured streaming without Delta Lake.
    # For this demo, we'll keep console, but the 'generate_tableau_data.py' script 
    # will handle the actual file generation for Tableau.
    
    query = df_kpi.writeStream \
        .format("console") \
        .outputMode("complete") \
        .start()
    
    return query

if __name__ == "__main__":
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Run the complete ETL pipeline: Bronze → Silver → Gold
    # In production, these would typically be separate jobs.
    # For this demo, we run Bronze layer to ingest raw data from Kafka.
    # Silver and Gold can be run separately after Bronze has data.
    
    try:
        print("=" * 60)
        print("Starting Fitbit Wellness ETL Pipeline")
        print("=" * 60)
        
        # Start Bronze layer (reads from Kafka, writes raw data)
        q_bronze = process_bronze(spark)
        
        # Uncomment below to run Silver layer (requires Bronze data to exist)
        # q_silver = process_silver(spark)
        
        # Uncomment below to run Gold layer (requires Silver data to exist)
        # q_gold = process_gold(spark)
        
        print("\nStreaming queries started. Press Ctrl+C to stop.")
        spark.streams.awaitAnyTermination()
    except KeyboardInterrupt:
        print("\nStopping streams...")
    except Exception as e:
        print(f"Streaming Error: {e}")

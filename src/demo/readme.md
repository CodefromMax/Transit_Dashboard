TO CONNECT TO THE DATABASE. USE THE FOLLOWING IN ORDER TO NOT HAVE TO CONFIGURE IP ON DB SIDE.

Download and install proxy executable, for M1 Mac below (use link https://cloud.google.com/sql/docs/mysql/sql-proxy#mac-m1 otherwise)

1. curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.14.3/cloud-sql-proxy.darwin.arm64
2. chmod +x cloud-sql-proxy

Add the service account key file under "Transit_Dashboard/src/helper" folder, then run this command to export the service account key file,
NOTE: Both the .json file and the config.cfg should be in this foler.

3. export GOOGLE_APPLICATION_CREDENTIALS="YOUR/PATH/TO/ROOT/HERE/Transit_Dashboard/src/helper/unique-perigee-442422-s0-17223e890fa1.json"

Run the proxy

4. ./cloud-sql-proxy unique-perigee-442422-s0:northamerica-northeast2:transit --port=3306

NOTE: The below requires you use transit-env3, which you can create using environment_python3_9-v2.yml

You can now connect to the db with either database_engine class or database_connector class. Database engine probably the better way to connect to the database, because it supports dataframes.

5. from helper.database_engine import DatabaseEngine
6. db = DatabaseEngine()

Execute queries, see src/demo for examples. Close connection when finnished

7. db.close_connection() 
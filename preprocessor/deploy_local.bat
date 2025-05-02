ECHO OFF
REM https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-clients
SET IMAGE_NAME=preprocessor_local_test
SET NETWORK_NAME=local_network
SET DB_CONTAINER=ra-centre_postgresql-db
SET REGION="us-west-1"

REM stop container if it exists
docker stop %IMAGE_NAME%
docker rm %IMAGE_NAME%

REM build image
docker buildx build --platform linux/amd64 --provenance=false -t docker-image:%IMAGE_NAME% .

REM create network
docker network disconnect %NETWORK_NAME% %DB_CONTAINER%
docker network rm %NETWORK_NAME%
docker network create %NETWORK_NAME%
docker network connect %NETWORK_NAME% %DB_CONTAINER%
SET DB_IP=172.18.0.2

REM start container
SETLOCAL EnableDelayedExpansion
docker run -d ^
    -v "%USERPROFILE%\.aws-lambda-rie:/aws-lambda" ^
    -p 9001:8080 ^
    --network %NETWORK_NAME% ^
    --add-host=localhost:%DB_IP% ^
    -e JUMP_HOST="%JUMP_HOST%" ^
    -e JUMP_USER="%JUMP_USER%" ^
    -e JUMP_HOST_SSH_KEY="!EC2_SSH_KEY!" ^
    -e AWS_ACCESS_KEY_ID="%AWS_ACCESS_KEY_ID%" ^
    -e AWS_SECRET_ACCESS_KEY="%AWS_SECRET_ACCESS_KEY%" ^
    --platform linux/amd64 ^
    --entrypoint /aws-lambda/aws-lambda-rie ^
    --name %IMAGE_NAME%^
    --stop-timeout 60 ^
    docker-image:"%IMAGE_NAME%" ^
    /usr/local/bin/python -m awslambdaric lambda_function.handler

REM test the lambda function
TIMEOUT 5
POWERSHELL -command "Invoke-WebRequest -Uri 'http://localhost:9001/2015-03-31/functions/function/invocations' -Method Post -Body '{\"write_to_db\": 1}' -ContentType 'application/json'"

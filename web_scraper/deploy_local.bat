ECHO OFF
REM https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-clients
SETLOCAL EnableDelayedExpansion
SET IMAGE_NAME=web_scraper_local_test
SET REGION="us-west-1"

REM stop container if it exists
docker stop %IMAGE_NAME%_local_test
docker rm %IMAGE_NAME%_local_test

REM build image
docker buildx build --platform linux/amd64 --provenance=false -t docker-image:%IMAGE_NAME%_test .
REM start container
docker run -d ^
    -v "%USERPROFILE%\.aws-lambda-rie:/aws-lambda" -p 9000:8080 ^
    -e JUMP_HOST="%JUMP_HOST%" ^
    -e JUMP_USER="%JUMP_USER%" ^
    -e JUMP_HOST_SSH_KEY="!EC2_SSH_KEY!" ^
    --platform linux/amd64 ^
    --entrypoint /aws-lambda/aws-lambda-rie ^
    --name %IMAGE_NAME%_local_test^
    --stop-timeout 60 ^
    docker-image:"%IMAGE_NAME%_test" ^
    /usr/local/bin/python -m awslambdaric lambda_function.handler

REM test the lambda function
TIMEOUT 5
POWERSHELL -command "Invoke-WebRequest -Uri 'http://localhost:9000/2015-03-31/functions/function/invocations' -Method Post -Body '{\"write_to_db\": 0}' -ContentType 'application/json'"

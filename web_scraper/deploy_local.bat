ECHO OFF
REM https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-clients
SETLOCAL EnableDelayedExpansion
SET IMAGE_NAME=web_scraper_local_test
SET REGION="us-west-1"

REM stop container if it exists
docker stop %IMAGE_NAME%
docker rm %IMAGE_NAME%

REM build image
docker buildx build --platform linux/amd64 --provenance=false -t docker-image:%IMAGE_NAME% .
REM start container
docker run -d ^
    -v "%USERPROFILE%\.aws-lambda-rie:/aws-lambda" -p 9000:8080 ^
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
POWERSHELL -command "Invoke-WebRequest -Uri 'http://localhost:9000/2015-03-31/functions/function/invocations' -Method Post -Body '{}' -ContentType 'application/json'"

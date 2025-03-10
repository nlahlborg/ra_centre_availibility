ECHO OFF
REM https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-clients
SET IMAGE_NAME=ra_centre2
SET REGION="us-west-1"

REM stop container if it exists
docker stop %IMAGE_NAME%_local_test
docker rm %IMAGE_NAME%_local_test

REM build image
docker buildx build --platform linux/amd64 --provenance=false -t docker-image:%IMAGE_NAME%_test .
REM start container
docker run --platform linux/amd64 -d -v "%USERPROFILE%\.aws-lambda-rie:/aws-lambda" -p 9000:8080 ^
    --entrypoint /aws-lambda/aws-lambda-rie ^
    --name %IMAGE_NAME%_local_test^
    docker-image:"%IMAGE_NAME%_test" ^
    /usr/local/bin/python -m awslambdaric lambda_function.handler
powershell -command "Invoke-WebRequest -Uri 'http://localhost:9000/2015-03-31/functions/function/invocations' -Method Post -Body '{\"write_to_db\": 0}' -ContentType 'application/json'"

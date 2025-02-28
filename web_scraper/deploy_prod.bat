ECHO OFF
REM https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions
SET IMAGE_NAME="ra_centre2"
SET REGION="us-west-1"

docker buildx build --platform linux/amd64 --provenance=false -t docker-image:"%IMAGE_NAME%_prod"
docker tag docker-image:"%IMAGE_NAME%_prod" %ECR_REPOSITORY_URI_PROD%:latest
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %ECR_REPOSITORY_URI_PROD%
docker push %ECR_REPOSITORY_URI_PROD%:latest

aws lambda update-function-code ^
  --function-name %IMAGE_NAME% ^
  --image-uri %ECR_REPOSITORY_URI_PROD%:latest ^
  --publish

REM aws lambda create-function ^
REM   --function-name %IMAGE_NAME% ^
REM   --package-type Image ^
REM   --code ImageUri=%ECR_REPOSITORY_URI%:latest ^
REM   --role arn:aws:iam::%AWS_ACCOUNT_ID%:role/lambda-ex
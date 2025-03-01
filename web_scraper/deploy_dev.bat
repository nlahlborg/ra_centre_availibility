ECHO OFF
REM https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions
SET IMAGE_NAME=ra_centre2
SET REGION="us-west-1"

docker buildx build --platform linux/amd64 --provenance=false -t docker-image:%IMAGE_NAME%_dev .
docker tag docker-image:"%IMAGE_NAME%_dev" %ECR_REPOSITORY_URI_DEV%:latest
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %ECR_REPOSITORY_URI_DEV%
docker push %ECR_REPOSITORY_URI_DEV%:latest

aws lambda update-function-code ^
  --function-name %IMAGE_NAME%_dev ^
  --image-uri %ECR_REPOSITORY_URI_DEV%:latest ^
  --publish

REM aws lambda create-function --function-name %IMAGE_NAME%_dev --package-type Image --code ImageUri=%ECR_REPOSITORY_URI_DEV%:latest --role arn:aws:iam::%AWS_ACCOUNT_ID%:role/lambda-ex
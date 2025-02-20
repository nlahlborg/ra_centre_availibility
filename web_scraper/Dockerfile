FROM public.ecr.aws/lambda/python:3.11

# Install build dependencies (for compiling packages if needed)
RUN yum install -y gcc gcc-c++ make python3-devel

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY .env ${LAMBDA_TASK_ROOT}/.env
COPY src ${LAMBDA_TASK_ROOT}/src
COPY tests ${LAMBDA_TASK_ROOT}/tests
COPY main.py ${LAMBDA_TASK_ROOT}/main.py
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/lambda_function.py
COPY secrets ${LAMBDA_TASK_ROOT}/secrets

# Remove build dependencies (to reduce image size)
RUN yum remove -y gcc gcc-c++ make python3-devel && yum clean all

# Set the entrypoint (command to run when the container starts)
CMD [ "lambda_function.lambda_handler" ]
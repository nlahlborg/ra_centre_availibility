# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.11 AS build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy application source code
RUN mkdir -p ${FUNCTION_DIR}
COPY src ${FUNCTION_DIR}/src
COPY main.py ${FUNCTION_DIR}/main.py
COPY lambda_function.py ${FUNCTION_DIR}/lambda_function.py
COPY secrets ${FUNCTION_DIR}/secrets
COPY .env ${FUNCTION_DIR}/.env

# Install the function's dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --target ${FUNCTION_DIR}

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.11-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Set the entrypoint
CMD [ "lambda_function.lambda_handler" ]
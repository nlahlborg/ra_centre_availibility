# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.13-slim-bookworm AS build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR
RUN mkdir -p ${FUNCTION_DIR}

# Install the function's dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --target ${FUNCTION_DIR} && \
    pip install --no-cache-dir awslambdaric && \
    find ${FUNCTION_DIR} -name "__pycache__" -type d -exec rm -rf {} + && \
    find ${FUNCTION_DIR} -name "*.pyc" -delete && \
    find ${FUNCTION_DIR} -name "*.pyo" -delete && \
    find ${FUNCTION_DIR} -name "*.dist-info" -type d -exec rm -rf {} + && \
    find ${FUNCTION_DIR} -name "*.egg-info" -type d -exec rm -rf {} + && \
    find ${FUNCTION_DIR} -name "tests" -type d -exec rm -rf {} + && \
    rm -rf ${FUNCTION_DIR}/*.dist-info ${FUNCTION_DIR}/*.egg-info

# Copy application source code
COPY src ${FUNCTION_DIR}/src
COPY main.py ${FUNCTION_DIR}/main.py
COPY lambda_function.py ${FUNCTION_DIR}/lambda_function.py
COPY secrets ${FUNCTION_DIR}/secrets
COPY ./.env ${FUNCTION_DIR}/.env

# Multi-stage build with distroless for even smaller image
FROM python:3.13-slim-bookworm

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT ["/usr/local/bin/python", "-m", "awslambdaric"]

# Set the entrypoint
CMD [ "lambda_function.handler" ]
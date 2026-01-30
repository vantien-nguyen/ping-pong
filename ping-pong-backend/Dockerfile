FROM python:3.14-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH" \
    APP_DIR=/app

# Install required build dependencies
RUN apk add --no-cache build-base

# Create virtual environment & install dependencies
RUN python -m venv ${VIRTUAL_ENV} && \
    pip install --upgrade pip && \
    pip install poetry

# Set working directory and install Python dependencies
WORKDIR ${APP_DIR}
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root && \
    rm -rf /root/.cache/pip && \
    find ${VIRTUAL_ENV} -name '__pycache__' -exec rm -r {} + && \
    apk del build-base

# Copy only necessary app files
COPY . .

EXPOSE 8000
CMD ["python", "ping-pong/manage.py", "runserver", "0.0.0.0:8000"]

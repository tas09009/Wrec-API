FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .

# Run migrations first (from bash script), then start guinicorn
CMD ["/bin/bash", "docker-entrypoint.sh"]


# Deployment on Render
# FROM python:3.10
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade -r requirements.txt
# COPY . .
# CMD ["/bin/bash", "docker-entrypoint.sh"]
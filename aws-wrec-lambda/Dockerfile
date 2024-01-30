# Use an AWS Lambda base image
FROM public.ecr.aws/lambda/python:3.10

# Copy the handler function and requirements file into the container
COPY handler.py .
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Set the CMD to your handler
CMD ["handler.handler"]

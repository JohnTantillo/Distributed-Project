# Set language and version
FROM python:3.8-alpine
# Establish working directory and move files to it
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
# Install required packages
RUN pip install -r requirements.txt
# Copy working directory to container
COPY . /app
# Run code
ENTRYPOINT [ "python" ]
CMD ["app.py" ]

# This dockerfile was created via a combination of online tutorials and previous projects
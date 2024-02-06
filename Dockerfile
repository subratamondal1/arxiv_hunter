FROM python:3.11.7-slim

RUN mkdir -p /app
# Copy the files from the arxiv-hunter/src directory to the /app directory inside the image
COPY .* /app
COPY requirements.txt /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
# Run the main.py file from the app subdirectory
CMD [ "src/main.py" ]
ENTRYPOINT [ "python" ]
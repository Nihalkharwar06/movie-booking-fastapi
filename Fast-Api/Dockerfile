FROM python:3.9.6-slim
WORKDIR /
COPY ./ .
COPY ./booming-tooling-384907-14d84f09490c.json ./key/booming-tooling-384907-14d84f09490c.json
RUN pip install firebase-admin
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
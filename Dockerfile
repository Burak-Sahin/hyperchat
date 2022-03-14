FROM python:alpine

RUN mkdir /hyperchat
COPY . /hyperchat/.
WORKDIR /hyperchat
RUN pip install -r requirements.txt --no-cache-dir && apk del build-dependencies

# For now, hardcoded 100 ports available
EXPOSE 8000-8100

CMD  [ "python", "app.py" ]

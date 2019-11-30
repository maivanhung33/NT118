FROM python

COPY . /mobile/

WORKDIR /mobile/

ENTRYPOINT ["python3", "/mobile/main/app.py"]

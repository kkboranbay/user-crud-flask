FROM python:3.5-onbuild
EXPOSE 9000
ENTRYPOINT ["python", "/usr/src/app/app.py"]

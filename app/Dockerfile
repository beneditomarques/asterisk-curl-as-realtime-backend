FROM tiangolo/uvicorn-gunicorn:python3.6
COPY ./app/ /app
COPY ./init_api.sh /
RUN chmod +x /init_api.sh  && pip install --no-cache-dir --upgrade -r /app/requirements.txt
CMD ["/init_api.sh"]
EXPOSE 8000
# Dockerfile

FROM python:3-onbuild

# COPY startup script into known file location in container
COPY start_server.sh /start_server.sh

EXPOSE 8000

# start the Gunicorn server
CMD ["/start_server.sh"]
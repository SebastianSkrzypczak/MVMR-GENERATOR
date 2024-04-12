FROM python:3.11-slim

RUN apt-get -q -y update
RUN apt-get install -y gcc

ENV USERNAME=mvmr
ENV WORKING_DIR=/app

WORKDIR ${WORKING_DIR}

COPY requirements.txt ${WORKING_DIR}

RUN groupadd ${USERNAME} && \
    useradd -g ${USERNAME} ${USERNAME}

RUN chown -R ${USERNAME}:${USERNAME} ${WORKING_DIR}
RUN chmod -R u=rwx ${WORKING_DIR}


USER ${USERNAME}
ENV PATH "$PATH:/home/${USERNAME}/.local/bin"

USER root
RUN apt-get update && apt-get install -y libpq-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

USER ${USERNAME}

ENV FLASK_APP=flask_app

COPY . ${WORKING_DIR}

EXPOSE 5000

CMD [ "flask", "run", "--reload", "--host=0.0.0.0", "--port=5000"]

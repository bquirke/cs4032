FROM centos

RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"

RUN python get-pip.py && \

    pip install Flask && \

    pip install Flask-PyMongo && \

    yum install -y gcc && \

    yum install -y libffi-devel && \

    yum install -y python-devel && \

    yum install -y openssl-devel && \

    pip install pycrypto && \

    pip install requests

COPY authenServer.py /src/authenServer.py
COPY serverSetup.py /src/serverSetup.py
COPY buildDb.py /src/buildDb.py

CMD ["python","/src/buildDb.py"]
CMD ["python","/src/authenServer.py"]

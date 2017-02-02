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


COPY directoryServer.py /src/directoryServer.py
COPY serverSetup.py /src/serverSetup.py
COPY buildDirDb.py /src/buildDirDb.py

CMD ["python","/src/buildDirDb.py"]
CMD ["python","/src/directoryServer.py"]
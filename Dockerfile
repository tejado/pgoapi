FROM python:3-onbuild

COPY ./pgoapi /pgoapi
COPY ./pokecli.py /pokecli.py

RUN pip install requests
RUN pip install protobuf
RUN pip install gpsoauth
RUN pip install geopy
RUN pip install s2sphere

ENTRYPOINT [ "python", "/pokecli.py" ]

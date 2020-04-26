FROM sohonet/alpyen:py3.7

ENV PYTHONIOENCODING=utf-8

RUN pip install -U pip
RUN pip3 install pipenv

ADD . /code
WORKDIR /code
RUN pipenv install

CMD pipenv run nameko run prog_image.service --config config.yaml

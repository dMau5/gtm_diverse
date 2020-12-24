FROM continuumio/miniconda3
LABEL maintainer="batyrshin-dinar@mail.ru"
WORKDIR /opt

COPY environment.yml .
RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "rdkit-env", "/bin/bash", "-c"]

COPY . .
WORKDIR /opt/diverse

EXPOSE 5000
ENTRYPOINT ["conda", "run", "-n", "rdkit-env", "python", "run.py"]

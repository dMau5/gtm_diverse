FROM continuumio/miniconda3
LABEL maintainer="batyrshin-dinar@mail.ru"
WORKDIR /opt

COPY environment.yml .
RUN conda env create -f environment.yml
ENV PATH /opt/conda/envs/rdkit-env/bin/:$PATH

COPY . .
WORKDIR /opt/diverse

EXPOSE 5000
ENTRYPOINT ["python", "run.py"]

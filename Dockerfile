FROM Python 3.10.6

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app
RUN pip install .
RUN make reset_local_files

CMD ["streamlit", "run", "frontend/app_b.py"]

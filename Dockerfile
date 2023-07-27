# Official Python base image
FROM python:3.10.6

# Working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install the Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the entire project directory into the container
COPY . /app
RUN pip install .

# Expose the port that Streamlit app is running on (by default, it's 8501)
EXPOSE 8501

# Command to run the Streamlit app when the container starts
CMD ["streamlit", "run", "frontend/app_b.py"]

# Use Miniconda base image
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment file and app source code
COPY . /app/

# Create conda environment
RUN conda env create -f environment.yml

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Activate env by default
SHELL ["conda", "run", "-n", "ehrml", "/bin/bash", "-c"]

# Expose port
EXPOSE 8000

# Command to run the FastAPI app using the conda env
CMD ["conda", "run", "--no-capture-output", "-n", "ehrml", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

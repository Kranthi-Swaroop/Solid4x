# Use a lightweight official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the RAG directory contents (including chroma_db and bm25_index)
COPY . .

# Expose port 8002, which is what the RAG server runs on
EXPOSE 8002

# Set the environment variable if needed
# ENV GEMINI_API_KEY="your_api_key_here"

# Command to run the RAG API server using Uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002"]

FROM python:3.12

# Prevent Python from creating .pyc files and output from being buffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first for better Docker layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create directories used by the application
RUN mkdir -p /app/verse_images /app/fonts

# Container starts by running the application
ENTRYPOINT ["python", "verse2image.py"]

#docker build -t it1013/verse2image .
# Linux
#docker run --rm \
#  -v "$(pwd)/verse_images:/app/verse_images" \
#  -v "$(pwd)/config.ini:/app/config.ini" \
#  -v "$(pwd)/nwt_S.epub:/app/nwt_S.epub:ro" \
#  it1013/verse2image "2 Samuel 21:3-6"
# Windows:
#docker run --rm `
#  -v "${PWD}/verse_images:/app/verse_images" `
#  -v "${PWD}/config.ini:/app/config.ini" `
#  -v "${PWD}/nwt_S.epub:/app/nwt_S.epub:ro" `
#  it1013/verse2image "2 Samuel 21:3-6"

#docker run --rm -v "${PWD}/verse_images:/app/verse_images" -v "${PWD}/config.ini:/app/config.ini" -v "${PWD}/nwt_S.epub:/app/nwt_S.epub:ro" it1013/verse2image "2 Samuel 21:3-6" --debug
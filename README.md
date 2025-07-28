# Doc2MD

[![Docker Pulls](https://img.shields.io/docker/pulls/felipefontoura/doc2md)](https://hub.docker.com/r/felipefontoura/doc2md)
[![Docker Image Size](https://img.shields.io/docker/image-size/felipefontoura/doc2md)](https://hub.docker.com/r/felipefontoura/doc2md)

Convert documents to Markdown format through a simple API service.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
docker run -d -p 5000:5000 felipefontoura/doc2md
```

### API Usage

Convert a document to Markdown:

```bash
curl -X POST \
  -H "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  --data-binary "@your_document.xlsx" \
  http://localhost:5000/convert
```

## ✨ Features

- Convert multiples files to Markdown (PDF, PowerPoint, Word, Excel, Images, Audio, HTML, CSV, JSON, XML and ZIP).
- OCR for PDF files.
- Simple REST API interface
- Docker support
- Easy deployment with Docker Stack

## 🛠️ Installation

### Using Docker Hub

1. Pull the image:

```bash
docker pull felipefontoura/doc2md
```

2. Run the container:

```bash
docker run -d -p 5000:5000 felipefontoura/doc2md
```

## 💻 Usage

### API Endpoints

#### Convert Document

```bash
curl -X POST \
 -H "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
 --data-binary "@your_document.xlsx" \
 http://localhost:5000/convert?ocr=true/false
```

## 📦 Deployment

### Docker Stack Deployment

Deploy using [Docker Stack](stack.yml):

```bash
docker stack deploy --prune --resolve-image always -c stack.yml doc2md
```

Example `doc2md.yml`:

```yaml
version: "3.7"
services:
  doc2md:
    image: felipefontoura/doc2md:latest
    environment:
      - OPENAI_API_KEY=sk-xxx
      - LLM_MODEL=gpt-4o-mini
      - WORKERS=4
      - TIMEOUT=0
    ports:
      - "5000:5000"
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
```

## 🔧 Development

1. Clone the repository
2. Build the Docker image locally
3. Run tests
4. Submit pull requests

## 📝 License

[MIT License](https://opensource.org/licenses/MIT)

---

Made with ❤️ by Felipe Fontoura

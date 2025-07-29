Convert documents to Markdown format through a simple API service.

### API Usage

Convert a document to Markdown:

```bash
curl -X POST \
  -H "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  --data-binary "@your_document.xlsx" \
  http://localhost:7001/convert
```

## ✨ Features

- Convert multiples files to Markdown (PDF, PowerPoint, Word, Excel, Images, Audio, HTML, CSV, JSON, XML and ZIP).
- OCR for PDF files.
- Simple REST API interface
- Docker support
- Easy deployment with Docker Stack

## 📦 Deployment

### Docker Stack Deployment

Deploy using [Docker Stack](stack.yml):

```bash
docker stack deploy --prune --resolve-image always -c stack.yml doc2md
```

Example `conversor-arquivos.yml`:

```yaml
version: "3.7"
services:
  doc2md:
    image: nickolas713/conversor-arquivos:latest
    environment:
      - OPENAI_API_KEY=sk-xxx (Pode excluir esta linha e criar a variavel direto no Coolify em "Environment Variables")
      - LLM_MODEL=gpt-4o-mini
      - WORKERS=4
      - TIMEOUT=0
    ports:
      - "7001:7001"
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

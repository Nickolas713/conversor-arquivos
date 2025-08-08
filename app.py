
import io
import pandas as pd
import pdfplumber
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_data_from_pdf(pdf_bytes: bytes):
    text_content = []
    tables_data = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            # Extrair texto
            text_content.append(page.extract_text())

            # Extrair tabelas
            tables = page.extract_tables()
            for table in tables:
                tables_data.append(table)

    return {"text": "\n".join(text_content), "tables": tables_data}

@app.route("/extract_pdf", methods=["POST"])
def extract_pdf():
    try:
        # A requisição do n8n deve enviar o PDF como binary data no corpo da requisição
        pdf_bytes = request.get_data()
        app.logger.info(f"Received request with Content-Type: {request.content_type}")
        app.logger.info(f"Received PDF data length: {len(pdf_bytes)} bytes")
        
        if not pdf_bytes:
            return jsonify({"error": "No PDF data provided"}), 400

        extracted_data = extract_data_from_pdf(pdf_bytes)
        return jsonify(extracted_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/convert_tables_to_csv", methods=["POST"])
def convert_tables_to_csv():
    try:
        data = request.get_json()
        tables = data.get("tables")

        if not tables:
            return jsonify({"error": "No tables data provided"}), 400

        csv_strings = []
        for i, table in enumerate(tables):
            # Converter cada tabela para um DataFrame e depois para CSV
            df = pd.DataFrame(table)
            csv_strings.append(df.to_csv(index=False, header=False))
        
        return jsonify({"csv_data": csv_strings})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7001)



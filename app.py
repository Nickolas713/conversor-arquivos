
import io
import os
import pandas as pd
import pdfplumber
import camelot
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_data_from_pdf(pdf_bytes: bytes):
    text_content = []
    tables_data = []
    temp_pdf_path = "temp_input.pdf"

    # Salva o PDF em um arquivo temporário para o Camelot
    try:
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Extração de texto com pdfplumber (para texto nativo)
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text_content.append(page.extract_text() or "")

        # Extração de tabelas com Camelot
        # Tenta o flavor 'stream' primeiro, que é bom para tabelas sem bordas
        try:
            camelot_tables = camelot.read_pdf(temp_pdf_path, pages="all", flavor="stream")
            for table in camelot_tables:
                tables_data.append(table.df.fillna("").values.tolist())
        except Exception as e:
            app.logger.warning(f"Camelot stream failed, trying lattice: {e}")
            # Se 'stream' falhar, tenta 'lattice' para tabelas com bordas
            try:
                camelot_tables = camelot.read_pdf(temp_pdf_path, pages="all", flavor="lattice")
                for table in camelot_tables:
                    tables_data.append(table.df.fillna("").values.tolist())
            except Exception as e_lattice:
                app.logger.error(f"Camelot lattice also failed: {e_lattice}")
                # Se ambos falharem, retorna tabelas vazias
                tables_data = []

    except Exception as e:
        app.logger.error(f"Error processing PDF: {e}")
        return {"text": "", "tables": []}
    finally:
        # Limpa o arquivo temporário
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

    return {"text": "\n".join(text_content), "tables": tables_data}

@app.route("/extract_pdf", methods=["POST"])
def extract_pdf():
    try:
        pdf_bytes = request.get_data()
        app.logger.info(f"Received request with Content-Type: {request.content_type}")
        app.logger.info(f"Received PDF data length: {len(pdf_bytes)} bytes")
        
        if not pdf_bytes:
            return jsonify({"error": "No PDF data provided"}), 400

        extracted_data = extract_data_from_pdf(pdf_bytes)
        return jsonify(extracted_data)

    except Exception as e:
        app.logger.error(f"Error in extract_pdf endpoint: {e}")
        import traceback
        app.logger.error(f"Traceback: {traceback.format_exc()}")
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
            df = pd.DataFrame(table)
            csv_strings.append(df.to_csv(index=False, header=False))
        
        return jsonify({"csv_data": csv_strings})

    except Exception as e:
        app.logger.error(f"Error in convert_tables_to_csv endpoint: {e}")
        import traceback
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



# Standard library imports
import asyncio
import mimetypes
import os
from typing import Tuple

# Third-party imports
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from markitdown import MarkItDown
from openai import OpenAI
from pyzerox import zerox

# Define supported file types and their MIME types
SUPPORTED_FORMATS = {
    "pdf": ["application/pdf"],
    "powerpoint": [
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ],
    "word": [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ],
    "excel": [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
    "image": [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/tiff",
        "image/webp",
    ],
    "audio": [
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "audio/m4a",
        "audio/mp3",
        "audio/aac",
    ],
    "html": ["text/html"],
    "text": [
        "text/plain",
        "text/csv",
        "application/json",
        "application/xml",
        "text/xml",
    ],
}

# Initialize Flask app
app = Flask(__name__)


def is_supported_format(content_type: str) -> Tuple[bool, str]:
    """
    Check if the content type is supported and return format type
    """
    for format_type, mime_types in SUPPORTED_FORMATS.items():
        if any(content_type.lower().startswith(mime) for mime in mime_types):
            return True, format_type
    return False, ""


def get_format_specific_prompt(format_type: str) -> str:
    """
    Return format-specific prompts for different file types
    """
    prompts = {
        "pdf": "Convert the following PDF page to markdown. Return only the markdown with no explanation text. Do not exclude any content from the page.",
        "image": "Analyze this image in detail, including any visible text, objects, and EXIF metadata if available. Extract text and nothing more.",
        "audio": "Transcribe this audio content and include any available metadata. Provide a detailed transcript of the speech.",
        "excel": "Extract and structure the data from this Excel file, maintaining table formats where possible.",
        "text": "Parse and structure this content, maintaining its original format while making it readable.",
        "html": "Extract the main content from this HTML, preserving important structure but removing unnecessary markup.",
    }
    return prompts.get(
        format_type,
        "Convert this document to markdown format, preserving structure and content.",
    )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route("/convert", methods=["POST"])
def convert():
    """
    Convert various file formats to markdown
    Supports: PDF, PowerPoint, Word, Excel, Images, Audio, HTML, and text-based formats

    Query Parameters:
        ocr (bool): Whether to use OCR processing for PDFs (default: True)
    """
    try:
        # Get the binary data and content type
        file_data = request.get_data()
        content_type = request.content_type

        if not file_data:
            return jsonify({"error": "No file data provided"}), 400

        # Check if the file format is supported
        is_supported, format_type = is_supported_format(content_type)
        if not is_supported:
            return jsonify(
                {
                    "error": f"Unsupported file type: {content_type}. Please provide a supported format."
                }
            ), 400

        # Determine file extension from content type
        extension = mimetypes.guess_extension(content_type) or ""
        temp_filename = f"temp_file{extension}"
        temp_path = os.path.join("uploads", temp_filename)

        # Save the binary data to a temporary file
        os.makedirs("uploads", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(file_data)

        try:
            model = os.getenv("LLM_MODEL", "gpt-4o-mini")
            format_prompt = get_format_specific_prompt(format_type)

            # Process PDF with OCR
            use_ocr = request.args.get("ocr", "true").lower() == "true"

            if format_type == "pdf" and use_ocr:
                output_dir = os.path.join("uploads", "output")
                os.makedirs(output_dir, exist_ok=True)

                result = asyncio.run(
                    zerox(
                        file_path=temp_path,
                        model=model,
                        output_dir=output_dir,
                        custom_system_prompt=format_prompt,
                        cleanup=True,
                        concurrency=3,
                    )
                )

                content = ""
                if hasattr(result, "pages") and result.pages:
                    content = "\n\n".join(page.content for page in result.pages)

                return jsonify({"content": content, "format": format_type, "ocr": True})

            # Process other formats using MarkItDown
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            md = MarkItDown(llm_client=client, llm_model=model)
            result = md.convert(temp_path, llm_prompt=format_prompt)

            return jsonify({"content": result.text_content, "format": format_type})

        finally:
            # Cleanup temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Run the Flask app
    app.run(host="0.0.0.0", port=7001)

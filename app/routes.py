import os
from pathlib import Path
from datetime import datetime
from flask import Blueprint, current_app, render_template, request, redirect, url_for, jsonify, abort
from werkzeug.utils import secure_filename
import json


from .ingest import ingest_file
from .preprocess import preprocess_texts
from . import corpus_store
from .topic_model import infer_topics
from .sentiment import infer_sentiment
from .extractive import extractive_summary
from .abstractive import abstractive_summary
from .dashboard_aggregation import aggregate_docs
from .wordcloud_utils import generate_wordcloud







bp = Blueprint("routes", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_PATH = BASE_DIR / "data" / "processed" / "corpus.json"



def _allowed_extension(filename: str) -> bool:
    if not filename:
        return False
    _, ext = os.path.splitext(filename.lower())
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {".txt", ".csv", ".docx"})

def make_unique_filename(directory: str | Path, filename: str) -> str:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    base, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while (directory / candidate).exists():
        candidate = f"{base} ({i}){ext}"
        i += 1
    return candidate

@bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("routes.upload"))

@bp.route("/upload", methods=["GET"])
def upload():
    return render_template("upload.html")


@bp.route("/upload", methods=["POST"])
def handle_upload():
    
    results = []
    try:
        text_column = request.form.get("text_column", "text") or "text"
        files = request.files.getlist("files")

        # defensive: ensure files is a list
        if files is None:
            files = []

        if len(files) == 0:
            # explicit return when no files selected
            return render_template("upload_result.html", results=[{
                "filename": None,
                "status": "FAIL",
                "message": "No files selected."
            }])

        # load existing corpus to compute next id
        existing = corpus_store.load_corpus()
        next_id = max([d.get("id", -1) for d in existing], default=-1) + 1

        upload_folder = current_app.config["UPLOAD_FOLDER"]

        for file_storage in files:
            try:
                # defensive: ensure file_storage exists and has filename
                if file_storage is None or not getattr(file_storage, "filename", None):
                    results.append({"filename": None, "status": "FAIL", "message": "Empty file input."})
                    continue

                original_name = file_storage.filename
                filename_safe = secure_filename(original_name)
                file_result = {"filename": original_name, "status": None, "message": "", "size": 0, "extracted": 0}

                if not filename_safe:
                    file_result.update({"status": "FAIL", "message": "Invalid filename after sanitization."})
                    results.append(file_result)
                    current_app.upload_logger.info(f"{original_name}\t0\tFAIL\tInvalid filename after sanitization")
                    continue

                # read bytes
                try:
                    data = file_storage.read()
                    if data is None:
                        raise ValueError("Read returned None")
                    size = len(data)
                    file_result["size"] = size
                except Exception as e:
                    file_result.update({"status": "FAIL", "message": f"Failed to read file stream: {e}"})
                    results.append(file_result)
                    current_app.upload_logger.info(f"{original_name}\t0\tFAIL\tFailed to read stream: {e}")
                    continue

                # checks
                if size == 0:
                    file_result.update({"status": "FAIL", "message": "File is empty."})
                    results.append(file_result)
                    current_app.upload_logger.info(f"{original_name}\t0\tFAIL\tFile is empty")
                    continue

                _, ext = os.path.splitext(original_name.lower())
                if ext not in current_app.config.get("ALLOWED_EXTENSIONS", {".txt", ".csv", ".docx"}):
                    file_result.update({"status": "FAIL", "message": f"Unsupported file type: {ext}"})
                    results.append(file_result)
                    current_app.upload_logger.info(f"{original_name}\t{size}\tFAIL\tUnsupported file type: {ext}")
                    continue

                if size > current_app.config.get("MAX_FILE_SIZE", 10*1024*1024):
                    file_result.update({"status": "FAIL", "message": f"File too large (max {current_app.config.get('MAX_FILE_SIZE')} bytes)."})
                    results.append(file_result)
                    current_app.upload_logger.info(f"{original_name}\t{size}\tFAIL\tFile too large")
                    continue

                # save uniquely
                try:
                    stored_name = make_unique_filename(upload_folder, filename_safe)
                    save_path = Path(upload_folder) / stored_name
                    with open(save_path, "wb") as out_f:
                        out_f.write(data)
                except Exception as e:
                    file_result.update({"status": "FAIL", "message": f"Failed to save file: {e}"})
                    results.append(file_result)
                    current_app.upload_logger.info(f"{original_name}\t{size}\tFAIL\tFailed to save file: {e}")
                    continue

                # ingest + preprocess
                try:
                    ingested = ingest_file(save_path, text_column=text_column)
                    processed_docs, next_id = preprocess_texts(ingested, source_file=stored_name, starting_id=next_id)



                    # attach timestamp + original filename 
                    ts = datetime.utcnow().isoformat() + "Z"

                    # collect texts for batch sentiment inference
                    sentiment_texts = [d["normalized_text"] for d in processed_docs]

                    # run sentiment once (vectorized, fast)
                    sentiments = infer_sentiment(sentiment_texts)

                    for doc, sentiment_result in zip(processed_docs, sentiments):
                        doc["sentiment"] = sentiment_result


                    for doc in processed_docs:
                        doc["original_filename"] = original_name
                        doc["upload_timestamp"] = ts

                        # #---- Topic Modeling ----
                        doc["topics"] = infer_topics(doc["tokens"])

                        
                        # #---- Sentiment Analysis ----
                        # sentiment model expects LIST[str]
                        sentiments = infer_sentiment(sentiment_texts)

                        for doc, sentiment_result in zip(processed_docs, sentiments):
                            doc["sentiment"] = sentiment_result

                        # store under a DIFFERENT key to avoid collisions
                        doc["sentiment"] = sentiment_result

                        # --- Extractive summarization ---
                        doc["extractive_summary"] = extractive_summary(
                            doc["raw_text"],  # IMPORTANT: raw text for now
                            # top_n=3
                        )
                       
                        # ---- Abstractive summarization ----

                        if doc.get("row_index", -1) == -1:
                            if doc.get("extractive_summary"):
                                structured_text = (
                                "Key points from the text are listed below.\n\n"
                                + "\n".join(f"- {s}" for s in doc["extractive_summary"])
                                )
                            else:
                                structured_text = doc["raw_text"]

                            doc["abstractive_summary"] = abstractive_summary(structured_text)
                        else:
                            doc["abstractive_summary"] = None

                    if processed_docs:
                        corpus_store.append_documents(processed_docs)

                    file_result.update({
                        "status": "SUCCESS",
                        "message": f"Uploaded and extracted {len(processed_docs)} document(s). Saved as {stored_name}",
                        "extracted": len(processed_docs)
                    })
                    current_app.upload_logger.info(f"{original_name}\t{size}\tSUCCESS\tSavedAs={stored_name}\tExtracted {len(processed_docs)} documents")
                except Exception as e:

                    import traceback
                    traceback.print_exc()   # <-- THIS IS CRITICAL

                    file_result.update({
                        "status": "FAIL",
                        "message": f"Ingest/Preprocess failed: {repr(e)}"
                    })

                results.append(file_result)

            except Exception as file_exc:
                # Catch per-file unexpected exceptions and continue with other files
                msg = f"Unexpected error processing file: {file_exc}"
                current_app.upload_logger.exception(msg)
                results.append({"filename": getattr(file_storage, "filename", None), "status": "FAIL", "message": msg})

        # final return: always returned
        return render_template("upload_result.html", results=results)

    except Exception as exc:
        # Global fallback: always return something, and log the stacktrace
        current_app.upload_logger.exception("Unhandled exception in handle_upload")
        # Return JSON if client expects JSON, otherwise return HTML template with error
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": "Server error during upload", "detail": str(exc)}), 500
        return render_template("upload_result.html", results=[{
            "filename": None,
            "status": "FAIL",
            "message": f"Server error: {exc}"
        }]), 500
    

@bp.route("/dashboard")
def dashboard():
    filename = request.args.get("file")
    if not filename:
        abort(400, "Missing file parameter")

    if not CORPUS_PATH.exists():
        abort(500, "Corpus not found")

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    # Filter docs belonging to this file
    docs = [d for d in corpus if d.get("original_filename") == filename]

    if not docs:
        abort(404, "No data found for this file")

    # Aggregate document-level insights
    aggregated = aggregate_docs(docs)

    # File overview (document-level only)
    file_info = {
        "name": filename,
        "type": filename.split(".")[-1].upper(),
        "rows": len(docs) if docs[0].get("row_index", -1) != -1 else None
    }

    # Summaries
    summaries = {
        "extractive": aggregated["summaries"]["extractive"],
        "abstractive": aggregated["summaries"]["abstractive"] #[:2000]
    }

    # ---- Word cloud generation ----
    BASE_DIR = Path(__file__).resolve().parent.parent

    wordcloud_path = BASE_DIR / "static" / "wordclouds" / f"{filename}.png"
    generate_wordcloud(aggregated["tokens"], wordcloud_path)



    topic_data = aggregated["topics"]
    sentiment_data = aggregated["sentiment"]

    return render_template(
        "dashboard.html",
        file_info=file_info,
        summaries=aggregated["summaries"],
        topic_data=topic_data,
        sentiment_data=sentiment_data,
        wordcloud_url=url_for("static", filename=f"wordclouds/{filename}.png")
    )




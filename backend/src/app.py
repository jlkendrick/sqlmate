from utils.generators import generate_query
from utils.db import get_cursor, get_timestamp
from utils.constants import PORT

from routers import auth, users

from models.queries.base import BaseQuery

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from typing import List, Any, Dict

appy = FastAPI()
appy.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sqlmate-ruddy.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

appy.include_router(router=auth.router, prefix="/auth")
appy.include_router(router=users.router, prefix="/users")

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://sqlmate-ruddy.vercel.app"], supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE"])

@app.route("/")
def home():
    return "Hello, world!"

# ================================= QUERY ENDPOINTS =================================
@app.route("/query", methods=["POST"])
def run_query():
    req: Dict = request.get_json()
    # with open("logs/input_log.txt", "w") as f:
    #     f.write(json.dumps(req, indent=4))

    # Validate the input data
    try:
        query: List[BaseQuery] = [BaseQuery(details) for details in req.get("tables", [])]
    except ValueError as e:
        print(e)
        return jsonify({"error_msg": e.args[0]}), 400


    query_body = generate_query(query, req.get("options", {}))
    # with open("logs/query_log.txt", "w") as f:
    #     f.write(query_body)

    try:
        with get_cursor() as cursor:
            cursor.execute(query_body)
            if cursor.description is None:
                return jsonify({"error": "No data found"}), 404
            column_names = [i[0] for i in cursor.description]
            rows: Any = cursor.fetchall()
    except mysql.connector.Error as e:
        print(e)
        return jsonify({"error_msg": f"Failed to run query: {query_body}"}), 500

    return jsonify(query_output_to_dict(rows, column_names, query_body, len(query))), 200


if __name__ == "__main__":
    port = PORT
    app.run(host="0.0.0.0", port=port, threaded=False, debug=True)
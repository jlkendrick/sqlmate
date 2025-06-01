from utils.db import get_cursor, get_timestamp
from utils.serialization import query_output_to_table
from utils.generators import generate_query
from models.http import StatusResponse, Table, QueryParams
from models.queries.base import BaseQuery

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header
from pydantic import BaseModel
import mysql.connector

router = APIRouter()

# ================================= QUERY ENDPOINTS =================================

class QueryRequest(BaseModel):
	query_params: List[QueryParams]
	options: Optional[Dict[str, Any]] = None
class QueryResponse(BaseModel):
	status: StatusResponse
	table: Table | None = None
@router.route("/", methods=["POST"])
def run_query(req: QueryRequest, authorization: Optional[str] = Header(None)):
	# with open("logs/input_log.txt", "w") as f:
	#     f.write(json.dumps(req, indent=4))

	# Validate the input data
	try:
		query: List[BaseQuery] = [BaseQuery(details) for details in req.query_params]
	except ValueError as e:
		print(e)
		return QueryResponse(
			status=StatusResponse(
				status="error",
				message=f"Invalid query parameters: {str(e)}"
			),
			table=None
		)


	query_body = generate_query(query, req.options or {})
	# with open("logs/query_log.txt", "w") as f:
	#     f.write(query_body)

	try:
		with get_cursor() as cursor:
			cursor.execute(query_body)
			if cursor.description is None:
				return QueryResponse(
					status=StatusResponse(
						status="error",
						message="No data found"
					),
					table=None
				)
			column_names = [i[0] for i in cursor.description]
			rows: Any = cursor.fetchall()
	except mysql.connector.Error as e:
		print(e)
		return QueryResponse(
			status=StatusResponse(
				status="error",
				message="Failed to execute query"
			),
			table=None
		)

	table: Table = query_output_to_table(rows, column_names, query_body, len(query))
	table.created_at = get_timestamp()
	return QueryResponse(
		status=StatusResponse(
			status="success",
			message="Query executed successfully"
		),
		table=table
	)
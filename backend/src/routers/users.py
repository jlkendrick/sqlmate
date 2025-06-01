from utils.db import get_cursor, get_timestamp
from utils.serialization import query_output_to_table
from utils.auth import check_user, get_token
from utils.generators import generate_update_query
from models.http import StatusResponse, Table, UpdateQueryParams
from models.queries.update import UpdateQuery
from models.metadata import metadata

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header
from pydantic import BaseModel
import mysql.connector

router = APIRouter()

# =============================== USER DATA ENDPOINTS ===============================

class SaveTableRequest(BaseModel):
	table_name: str
	query: str
class SaveTableResponse(StatusResponse):
	status: StatusResponse
@router.route("/save_table", methods=["POST"])
def save_table(req: SaveTableRequest, authorization: Optional[str] = Header(None)):
	# Check the authentication of the user
	token = authorization
	username, error = check_user(token)
	if error:
		return SaveTableResponse(
			status=StatusResponse(
				status="error",
				message=error
			)
		)

	table_name = req.table_name
	query = req.query

	if not table_name or not query:
		return SaveTableResponse(
			status=StatusResponse(
				status="error",
				message="Missing table name or query"
			)
		)
	
	
	# Execute the stored procedure to create the table (this checks if the table already exists as well)
	created_at = get_timestamp()
	with get_cursor("sqlmate") as cur:
		try:
			cur.callproc("save_user_table", [username, table_name, created_at, query])
		except mysql.connector.IntegrityError as e:
			print(e)
			return SaveTableResponse(
				status=StatusResponse(
					status="warning",
					message="Table already exists"
				)
			)
		except mysql.connector.Error as e:
			print(e)
			return SaveTableResponse(
				status=StatusResponse(
					status="error",
					message="Failed to create table"
				)
			)
		
	# After we save the table, we need to update metadata to include the new table
	full_table_name = f"u_{username}_{table_name}"
	metadata.add_table(full_table_name)
		
	return SaveTableResponse(
		status=StatusResponse(
			status="success",
			message="Table saved successfully"
		)
	)

class DeleteTableRequest(BaseModel):
	table_names: str | list[str]
class DeleteTableResponse(BaseModel):
	status: StatusResponse
	deleted_tables: list[str] | None = None
@router.route("/delete_table", methods=["POST"])
def drop_table(req: DeleteTableRequest, authorization: Optional[str] = Header(None)):
	# Check the authentication of the user
	token = get_token(authorization)
	username, error = check_user(token)
	if error:
		return DeleteTableResponse(
			status=StatusResponse(
				status="error",
				message=error
			)
		)

	# We allow both a single table name and a list of table names, however we convert it to a list regardless for ease of processing
	temp = req.table_names
	if isinstance(temp, str) and temp:
		table_names = [temp]
	elif isinstance(temp, list):
		table_names = temp
	else:
		return DeleteTableResponse(
			status=StatusResponse(
				status="error",
				message="Invalid table names format"
			)
		)
	
	if not table_names:
		return DeleteTableResponse(
			status=StatusResponse(
				status="error",
				message="No table names provided"
			)
		)
	
	# Execute the query to delete the entries from the user_tables table, which triggers insertion into tables_to_drop
	with get_cursor("sqlmate") as cur:
		try:
			for table_name in table_names:
				if not table_name:
					return DeleteTableResponse(
						status=StatusResponse(
							status="error",
							message="Invalid table name"
						)
					)
				cur.execute("DELETE FROM user_tables WHERE username = %s AND table_name = %s", (username, table_name))
		except mysql.connector.Error as e:
			print(e)
			return DeleteTableResponse(
				status=StatusResponse(
					status="error",
					message="Failed to drop table"
				)
			)
	
	# Execute the stored procedure to drop the tables that were marked for deletion in the previous step
	with get_cursor("sqlmate") as cur:
		try:
			cur.callproc("process_tables_to_drop")
		except mysql.connector.Error as e:
			print(e)
			return DeleteTableResponse(
				status=StatusResponse(
					status="error",
					message="Failed to drop table"
				)
			)
					
	return DeleteTableResponse(
		status=StatusResponse(
			status="success",
			message="Table(s) dropped successfully"
		),
		deleted_tables=table_names
	)

class GetTablesResponse(BaseModel):
	status: StatusResponse
class GetTablesReponse(GetTablesResponse):
	tables: List[Dict[str, str]] | None = None
@router.route("/get_tables", methods=["GET"])
def get_tables(authorization: Optional[str] = Header(None)) -> GetTablesReponse:
	# Check the authentication of the user
	token = get_token(authorization)
	username, error = check_user(token)
	if error:
		return GetTablesReponse(
			status=StatusResponse(
				status="error",
				message=error
			)
		)

	rows = []
	with get_cursor("sqlmate") as cur:
		try:
			cur.execute("SELECT table_name, created_at FROM user_tables WHERE username = %s", (username,))
			rows: List[Any] = cur.fetchall()
		except mysql.connector.Error as e:
			print(e)
			return GetTablesReponse(
				status=StatusResponse(
					status="error",
					message="Failed to get tables"
				)
			)
	if not rows:
		return GetTablesReponse(
			status=StatusResponse(
				status="success",
				message="No tables found"
			)
		)
	
	tables: List[Dict[str, str]] = [{"table_name": row[0], "created_at": row[1]} for row in rows]
	return GetTablesReponse(
		status=StatusResponse(
			status="success",
			message="Tables retrieved successfully"
		),
		tables=tables
	)

class GetTableDataRequest(BaseModel):
	table_name: str
class GetTableDataResponse(BaseModel):
	status: StatusResponse
	table: Table | None = None
@router.route("/get_table_data", methods=["GET"])
def get_table_data(req: GetTableDataRequest, authorization: Optional[str] = Header(None)) -> GetTableDataResponse:
	# Check the authentication of the user
	token = get_token(authorization)
	username, error = check_user(token)
	if error:
		return GetTableDataResponse(
			status=StatusResponse(
				status="error",
				message=error
			)
		)

	table_name = req.table_name
	if not table_name:
		return GetTableDataResponse(
			status=StatusResponse(
				status="error",
				message="Missing table name"
			)
		)
	
	formatted_table_name = f"u_{username}_{table_name}"
	query = f"SELECT * FROM {formatted_table_name};"
	with get_cursor("sqlmate") as cur:
		try:
			cur.execute(query)
			rows: List[Any] = cur.fetchall()
			if cur.description is None:
				return GetTableDataResponse(
					status=StatusResponse(
						status="error",
						message="No data found"
					)
				)
			column_names: List[str] = [i[0] for i in cur.description]
		except mysql.connector.Error as e:
			print(e)
			return GetTableDataResponse(
				status=StatusResponse(
					status="error",
					message="Failed to get table data"
				)
			)
	if not rows:
		return GetTableDataResponse(
			status=StatusResponse(
				status="success",
				message="No data found"
			)
		)
	
	table = query_output_to_table(rows, column_names, query, 1)
	table.created_at = get_timestamp()
	return GetTableDataResponse(
		status=StatusResponse(
			status="success",
			message="Table data retrieved successfully"
		),
		table=table
	)

class UpdateTableRequest(BaseModel):
	query_params: UpdateQueryParams
class UpdateTableResponse(BaseModel):
	status: StatusResponse
	rows_affected: int | None = None
@router.route("/update_table", methods=["POST"])
def update(req: UpdateTableRequest, authorization: Optional[str] = Header(None)):
	# Check the authentication of the user
	token = get_token(authorization)
	username, error = check_user(token)
	if error:
		return UpdateTableResponse(
			status=StatusResponse(
				status="error",
				message=error
			)
		)

	# Validate the input data
	try:
		query = UpdateQuery(req.query_params, username)
	except ValueError as e:
		print(e)
		return UpdateTableResponse(
			status=StatusResponse(
				status="error",
				message=str(e)
			)
		)


	query_body = generate_update_query(query)
	# with open("logs/update_log.txt", "w") as f:
	#     f.write(query_body)

	if not query_body:
		return UpdateTableResponse(
			status=StatusResponse(
				status="error",
				message="Invalid query"
			)
		)
	
	try:
		with get_cursor("sqlmate") as cursor:
			cursor.execute(query_body)
			result = cursor.rowcount
	except mysql.connector.Error as e:
		print(e)
		return UpdateTableResponse(
			status=StatusResponse(
				status="error",
				message="Failed to update table"
			)
		)

	return UpdateTableResponse(
		status=StatusResponse(
			status="success",
			message="Table updated successfully"
		),
		rows_affected=result
	)
def query_output_to_dict(query_output: list[tuple], column_names: list[str], query_body: str, num_tables: int) -> dict:
	if not query_output:
		return {}
	
	# If the query is a single table query, we can remove the table name from the column names
	if num_tables == 1:
		cleaned_column_names = []
		for col_name in column_names:
			for i in range(len(col_name)):
				if col_name[i] == "_":
					cleaned_column_names.append(col_name[i + 1:])
					break
			else: # Executed if the for loop is not broken out of (even though it should be)
				cleaned_column_names.append(col_name)
		column_names = cleaned_column_names

	# Convert each row to a dictionary
	json_output = [
		{column_names[i]: row[i] for i in range(len(column_names))}
		for row in query_output
	]

	# This is what the frontend expects to be able to deserialize into the table
	response = {
		'table': {
			'columns': column_names, 
			'rows': json_output
		},
		'query': query_body
	}
	return response
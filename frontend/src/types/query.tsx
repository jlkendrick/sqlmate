export interface QueryResponse {
  table: Table;
  query: string;
  error?: string;
}

export interface Table {
  columns: string[];
  rows: any[];
  error?: string;
}

export interface SaveTableRequest {
  table_name: string;
  query: string;
}

export interface SaveTableResponse {
  success: boolean;
  message: string;
}

export interface DeleteTableResponse {
  success: boolean;
  message: string;
  deleted_tables: string[];
}

// Table Update interfaces
export interface TableUpdateAttribute {
  attribute: string;
  value: string | number | boolean | null;
}

export interface TableUpdateConstraint {
  attribute: string;
  operator: string;
  value: string | number | boolean | null;
}

export interface TableUpdateRequest {
  table: string;
  updates: TableUpdateAttribute[];
  constraints: TableUpdateConstraint[];
}

export interface TableUpdateResponse {
  success: boolean;
  message: string;
  rows_affected?: number;
}

export interface VisualQueryAttribute {
  attribute: string;
  alias: string;
}

export interface VisualQueryConstraint {
  attribute: string;
  operator: string;
  value: string | number | boolean | Date;
}

export interface VisualQueryAggregation {
  attribute: string;
  type: string;
}

export interface VisualQueryOrderBy {
  attribute: string;
  sort: string;
}

export interface VisualQueryTable {
  table: string;
  attributes: VisualQueryAttribute[];
  constraints: VisualQueryConstraint[];
  group_by: string[];
  aggregations: VisualQueryAggregation[];
}

export interface VisualQueryOptions {
  limit?: number;
  order_by?: VisualQueryOrderBy[];
}

export interface VisualQueryRequest {
  tables: VisualQueryTable[];
  options?: VisualQueryOptions;
}

export type VisualQuery = VisualQueryTable[];

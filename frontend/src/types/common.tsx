/**
 * These interfaces match the backend Pydantic models
 */

export type StatusType = "success" | "error" | "warning";

export interface StatusResponse {
  status: StatusType;
  message?: string;
  code?: number;
}

export interface Table {
  query: string;
  created_at?: string;
  columns: string[];
  rows: any[];
}

export interface QueryResponse {
  status: StatusResponse;
  table?: Table;
}

export interface SaveTableRequest {
  table_name: string;
  query: string;
}

export interface SaveTableResponse {
  status: StatusResponse;
}

export interface DeleteTableResponse {
  status: StatusResponse;
  deleted_tables?: string[];
}

// Table Update interfaces
export interface TableUpdateAttribute {
  attribute: string;
  value: string;
}

export interface TableUpdateConstraint {
  attribute: string;
  operator: string;
  value: string;
}

export interface UpdateQueryParams {
  table: string;
  updates: TableUpdateAttribute[];
  constraints: TableUpdateConstraint[];
}

export interface UpdateTableRequest {
  query_params: UpdateQueryParams;
}

export interface UpdateTableResponse {
  status: StatusResponse;
  rows_affected?: number;
}

export interface QueryAttribute {
  attribute: string;
  alias: string;
}

export interface QueryConstraint {
  attribute: string;
  operator: string;
  value: string;
}

export interface QueryAggregation {
  attribute: string;
  type: string;
}

export interface QueryParams {
  table: string;
  attributes: QueryAttribute[];
  constraints?: QueryConstraint[];
  group_by?: string[];
  aggregations?: QueryAggregation[];
}

export interface QueryRequest {
  query_params: QueryParams[];
  options?: {
    limit?: number;
    order_by?: Array<{
      table_name: string;
      attribute: string;
      sort: string;
    }>;
  };
}

// Keeping these for compatibility with existing code
export interface VisualQueryAttribute extends QueryAttribute {}
export interface VisualQueryConstraint extends QueryConstraint {}
export interface VisualQueryAggregation extends QueryAggregation {}
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
  query_params: QueryParams[];
  options?: {
    limit?: number;
    order_by?: Array<{
      table_name: string;
      attribute: string;
      sort: string;
    }>;
  };
}

// Backwards compatibility
export type VisualQuery = VisualQueryTable[];

// Legacy type mapping for backward compatibility
export type TableUpdateRequest = UpdateTableRequest;
export type TableUpdateResponse = UpdateTableResponse;

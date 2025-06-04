import { BaseApiClient } from "./baseClient";
import {
  Table,
  SaveTableRequest,
  SaveTableResponse,
  DeleteTableRequest,
  DeleteTableResponse,
  QueryResponse,
} from "@/types/http";

interface UserTable {
  table_name: string;
  created_at: string;
}

interface GetTablesResponse {
  details: {
    status: "success" | "error" | "warning";
    message?: string;
  };
  tables?: UserTable[];
}

export class TableApiService extends BaseApiClient {
  constructor() {
    super();
  }

  /**
   * Get user's saved tables
   */
  async getTables(): Promise<GetTablesResponse> {
    return await this.get<GetTablesResponse>("/users/get_tables");
  }

  /**
   * Get data for a specific table
   */
  async getTableData(tableName: string): Promise<QueryResponse> {
    return await this.get<QueryResponse>(
      `/users/get_table_data?table_name=${encodeURIComponent(tableName)}`
    );
  }

  /**
   * Save a table from query results
   */
  async saveTable(saveTableData: SaveTableRequest): Promise<SaveTableResponse> {
    return this.post<SaveTableRequest, SaveTableResponse>(
      "/users/save_table",
      saveTableData
    );
  }

  /**
   * Delete one or more tables
   */
  async deleteTables(tableNames: DeleteTableRequest): Promise<DeleteTableResponse> {
    return this.post<DeleteTableRequest, DeleteTableResponse>(
      "/users/delete_table",
      tableNames
    );
  }

  /**
   * Get table data for export (CSV, etc.)
   */
  async getTableDataForExport(tableName: string): Promise<QueryResponse> {
    return await this.get<QueryResponse>(
      `/users/get_table_data?table_name=${encodeURIComponent(tableName)}`
    );
  }
}

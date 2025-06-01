import { BaseApiClient } from "./baseClient";
import {
  Table,
  SaveTableRequest,
  SaveTableResponse,
  DeleteTableResponse,
  QueryResponse,
} from "@/types/common";

interface UserTable {
  table_name: string;
  created_at: string;
}

interface GetTablesResponse {
  status: {
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
    console.log("Fetching tables...");
    try {
      const response = await this.get<GetTablesResponse>("/users/get_tables");
      console.log("Tables fetched successfully:", response);
      return response;
    } catch (error) {
      console.error("Error fetching tables:", error);
      // Return empty tables array if 404
      if (error instanceof Error && error.message.includes("404")) {
        return {
          status: { status: "success", message: "No tables found" },
          tables: [],
        };
      }
      throw error;
    }
  }

  /**
   * Get data for a specific table
   */
  async getTableData(tableName: string): Promise<Table | undefined> {
    const response = await this.get<QueryResponse>(
      `/users/get_table_data?table_name=${encodeURIComponent(tableName)}`
    );
    return response.table;
  }

  /**
   * Save a table from query results
   */
  async saveTable(saveTableData: SaveTableRequest): Promise<SaveTableResponse> {
    return this.post<SaveTableResponse, SaveTableRequest>(
      "/users/save_table",
      saveTableData
    );
  }

  /**
   * Delete one or more tables
   */
  async deleteTables(tableNames: string[]): Promise<DeleteTableResponse> {
    return this.post<DeleteTableResponse>("/users/delete_table", {
      table_names: tableNames,
    });
  }

  /**
   * Get table data for export (CSV, etc.)
   */
  async getTableDataForExport(tableName: string): Promise<Table | undefined> {
    const response = await this.get<QueryResponse>(
      `/users/get_table_data?table_name=${encodeURIComponent(tableName)}`
    );
    return response.table;
  }
}

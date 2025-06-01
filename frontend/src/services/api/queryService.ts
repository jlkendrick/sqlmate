import { BaseApiClient } from "./baseClient";
import {
  QueryRequest,
  QueryResponse,
  UpdateTableRequest,
  UpdateTableResponse,
} from "@/types/common";

export class QueryApiService extends BaseApiClient {
  constructor() {
    super();
  }

  /**
   * Run a visual query (SELECT)
   */
  async runQuery(queryData: QueryRequest): Promise<QueryResponse> {
    return this.post<QueryResponse, QueryRequest>("/query", queryData);
  }

  /**
   * Run a table update (UPDATE)
   */
  async updateTable(
    updateData: UpdateTableRequest
  ): Promise<UpdateTableResponse> {
    return this.post<UpdateTableResponse, UpdateTableRequest>(
      "/users/update_table",
      updateData
    );
  }
}

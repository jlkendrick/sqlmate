import { BaseApiClient } from "./baseClient";
import {
  QueryRequest,
  QueryResponse,
  UpdateTableRequest,
  UpdateTableResponse,
} from "@/types/http";

export class QueryApiService extends BaseApiClient {
  constructor() {
    super();
  }

  /**
   * Run a visual query (SELECT)
   */
  async runQuery(queryData: QueryRequest): Promise<QueryResponse> {
    return this.post<QueryRequest, QueryResponse>("/query", queryData);
  }

  /**
   * Run a table update (UPDATE)
   */
  async updateTable(
    updateData: UpdateTableRequest
  ): Promise<UpdateTableResponse> {
    return this.post<UpdateTableRequest, UpdateTableResponse>(
      "/users/update_table",
      updateData
    );
  }
}

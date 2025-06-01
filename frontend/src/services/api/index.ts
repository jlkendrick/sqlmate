import { AuthApiService } from "./authService";
import { TableApiService } from "./tableService";
import { QueryApiService } from "./queryService";

// Create and export singleton instances of each service
export const authService = new AuthApiService();
export const tableService = new TableApiService();
export const queryService = new QueryApiService();

// For direct import if needed
export { AuthApiService, TableApiService, QueryApiService };

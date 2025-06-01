// Example of using the API services

import { authService, tableService, queryService } from "@/services/api";
import { runVisualQuery } from "@/services/visualQueryService";

/**
 * Example auth flow
 */
async function authExample() {
  try {
    // Register a new user
    await authService.register("username", "password", "email@example.com");

    // Login
    const loginResponse = await authService.login("username", "password");
    // Store token from response
    localStorage.setItem("token", loginResponse.token);

    // Get current user info
    const userInfo = await authService.getCurrentUser();
    console.log("User info:", userInfo);
  } catch (error) {
    console.error("Auth error:", error);
  }
}

/**
 * Example table management
 */
async function tableExample() {
  try {
    // Get all user tables
    const tablesResponse = await tableService.getTables();
    console.log("User tables:", tablesResponse.tables);

    // Get data for a specific table
    const tableData = await tableService.getTableData("my_table");
    console.log("Table data:", tableData);

    // Save a new table
    await tableService.saveTable({
      table_name: "new_table",
      query: "SELECT * FROM users",
    });

    // Delete tables
    await tableService.deleteTables(["table_to_delete"]);
  } catch (error) {
    console.error("Table error:", error);
  }
}

/**
 * Example query operations
 */
async function queryExample() {
  try {
    // Run a query directly
    const queryData = {
      query_params: [
        {
          table: "users",
          attributes: [{ attribute: "username", alias: "" }],
          constraints: [{ attribute: "id", operator: ">", value: "5" }],
        },
      ],
    };

    const queryResult = await queryService.runQuery(queryData);
    console.log("Query result:", queryResult);

    // Update a table
    const updateData = {
      query_params: {
        table: "users",
        updates: [{ attribute: "status", value: "active" }],
        constraints: [{ attribute: "id", operator: "=", value: "1" }],
      },
    };

    const updateResult = await queryService.updateTable(updateData);
    console.log("Update result:", updateResult);
  } catch (error) {
    console.error("Query error:", error);
  }
}

// Using the visual query service
async function visualQueryExample(droppedTables: any[], limit?: number) {
  try {
    const result = await runVisualQuery(droppedTables, limit);
    console.log("Visual query result:", result);
  } catch (error) {
    console.error("Visual query error:", error);
  }
}

// These functions would be called from your React components as needed

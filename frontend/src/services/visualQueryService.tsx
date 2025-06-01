import { queryService } from "./api";
import { TableItem } from "@/components/tablePanel";
import { Column } from "@/components/tableCustomizationPanel";
import {
  QueryResponse,
  QueryParams,
  QueryRequest,
  QueryAttribute,
  QueryConstraint,
  QueryAggregation,
} from "@/types/common";

interface OrderByPriorityItem {
  tableId: string;
  tableName: string;
  columnName: string;
  direction: "ASC" | "DESC";
}

export async function runVisualQuery(
  droppedTables: TableItem[],
  limit?: number,
  orderByPriority?: OrderByPriorityItem[]
): Promise<QueryResponse> {
  const serializedData = serializeTablesForQuery(
    droppedTables,
    limit,
    orderByPriority
  );
  console.log("Serialized Data:", JSON.stringify(serializedData, null, 2));
  const response = await queryService.runQuery(serializedData);
  return response;
}

function serializeTablesForQuery(
  droppedTables: TableItem[],
  limit?: number,
  orderByPriority?: OrderByPriorityItem[]
): QueryRequest {
  const query_params = droppedTables.map((table): QueryParams => {
    // Ensure we're using the customColumns array if it exists, otherwise use a default empty array
    const columns = (table.customColumns || []) as Column[];

    // Check if we need to include all original columns from the table
    // If no customColumns are defined or the array is empty, include all original columns
    const shouldIncludeAllOriginalColumns = columns.length === 0;

    // Create the table object with appropriate attributes
    return {
      table: table.name,

      // Include all columns, whether they have an alias or not
      attributes: shouldIncludeAllOriginalColumns
        ? table.columns.map((col) => ({
            attribute: col.name,
            alias: "", // Empty alias for original columns
          }))
        : columns.map((col) => ({
            attribute: col.name,
            alias: col.alias || "", // Use empty string if alias is not provided
          })),

      // Other properties remain the same
      constraints: columns
        .filter((col) => col.constraint?.operator && col.constraint?.value)
        .map((col) => ({
          attribute: col.name,
          operator: col.constraint.operator,
          value: String(col.constraint.value), // Convert to string to match backend expectations
        })),

      group_by: columns.filter((col) => col.groupBy).map((col) => col.name),

      aggregations: columns
        .filter((col) => col.aggregate)
        .map((col) => ({
          attribute: col.name,
          type: col.aggregate,
        })),
    };
  });

  // Create the request object with options
  const request: QueryRequest = {
    query_params: query_params,
    options: {
      limit: limit && limit <= 1000 ? limit : 1000,
    },
  };

  // If we have a priority list, add it to the options
  if (orderByPriority && orderByPriority.length > 0) {
    // Create prioritized order by list
    if (!request.options) {
      request.options = {};
    }
    request.options.order_by = orderByPriority.map((item) => ({
      table_name: item.tableName,
      attribute: item.columnName, // Use the column name directly
      sort: item.direction,
    }));
  }

  return request;
}

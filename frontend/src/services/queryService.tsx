import { postVisualQuery } from "@/lib/apiClient";
import { TableItem } from "@/components/tablePanel";
import { Column } from "@/components/tableCustomizationPanel";
import {
  QueryResponse,
  VisualQuery,
  VisualQueryTable,
  VisualQueryRequest,
  VisualQueryOrderBy,
} from "@/types/query";

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
  console.log("Serialized Data:", serializedData);
  const response = await postVisualQuery(serializedData);
  return response;
}

function serializeTablesForQuery(
  droppedTables: TableItem[],
  limit?: number,
  orderByPriority?: OrderByPriorityItem[]
): VisualQueryRequest {
  const tables = droppedTables.map((table): VisualQueryTable => {
    // Ensure we're using the customColumns array if it exists, otherwise use a default empty array
    const columns = (table.customColumns || []) as Column[];

    return {
      table: table.name,

      // Include all columns, whether they have an alias or not
      attributes: columns.map((col) => ({
        attribute: col.name,
        alias: col.alias || "", // Use empty string if alias is not provided
      })),

      // Other properties remain the same
      constraints: columns
        .filter((col) => col.constraint?.operator && col.constraint?.value)
        .map((col) => ({
          attribute: col.name,
          operator: col.constraint.operator,
          value: col.constraint.value,
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

  // Create the request object
  const request: VisualQueryRequest = {
    tables,
  };

  // Add options
  request.options = {};

  // If we have a priority list, add it to the options
  if (orderByPriority && orderByPriority.length > 0) {
    // Create prioritized order by list
    const prioritizedOrderBy = orderByPriority.map((item) => ({
      table_name: item.tableName,
      attribute: item.columnName, // Use the column name directly
      sort: item.direction,
    }));

    request.options.order_by = prioritizedOrderBy;
  }

  // If the limit is not provided, or is greater than 1000, cap it at 1000
  request.options.limit = limit && limit <= 1000 ? limit : 1000;

  return request;
}

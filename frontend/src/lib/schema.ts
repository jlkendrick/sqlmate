// Utility functions for the application
import { TableItem } from "@/components/tablePanel";
import schema from "@/../public/db_schema.json";

// Function to load database schema from JSON
export function loadDatabaseSchema(): TableItem[] {
  try {
		// Directly return the schema from the JSON file
		return schema.map((table: any) => ({
			id: `${table.table}-table`,
			name: table.table,
			columns: table.columns.map((col: any) => ({
				name: col.name,
				type: col.type,
			})),
		}));
  } catch (error) {
    console.error("Error loading database schema:", error);
    return []; // Return empty array on error
  }
}

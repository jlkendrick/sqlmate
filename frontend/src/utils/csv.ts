// filepath: /Users/jameskendrick/Code/Courses/cs411/sp25-cs411-team006-0.1xDevelopers/frontend/src/utils/csv.ts
import { Table } from "@/types/http";

/**
 * Converts table data to CSV format
 * @param table The table data to convert
 * @returns CSV formatted string
 */
export function convertTableToCSV(table: Table): string {
  if (!table || !table.columns || !table.rows) {
    return "";
  }

  // Create header row
  const headerRow = table.columns
    .map((column) => `"${column.replace(/"/g, '""')}"`)
    .join(",");

  // Create data rows
  const dataRows = table.rows.map((row) => {
    return table.columns
      .map((column) => {
        const value = row[column];
        // Handle different data types
        if (value === null || value === undefined) {
          return "";
        } else if (typeof value === "string") {
          // Escape quotes in strings by doubling them
          return `"${value.replace(/"/g, '""')}"`;
        } else {
          return value;
        }
      })
      .join(",");
  });

  // Combine header and data
  return [headerRow, ...dataRows].join("\n");
}

/**
 * Downloads table data as a CSV file
 * @param table The table data to download
 * @param filename The name of the CSV file
 */
export function downloadTableAsCSV(table: Table, filename: string): void {
  const csv = convertTableToCSV(table);
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.csv`);
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

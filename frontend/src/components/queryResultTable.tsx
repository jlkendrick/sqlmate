import React from "react";
import type { Table } from "@/types/http";
import { AlertCircle } from "lucide-react";

type Props = {
  data: Table;
};

export const QueryResultTable: React.FC<Props> = ({ data }) => {
  const { columns, rows, error } = data;

  // If there's an error, display it prominently
  if (error) {
    return (
      <div className="p-4 rounded-md bg-red-50 border border-red-200 text-red-700">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span className="font-medium">Query Error: </span>
          <span className="ml-1">{error}</span>
        </div>
      </div>
    );
  }

  if (!columns || !rows || !columns.length || !rows.length)
    return <p>No results found.</p>;

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 shadow">
      <table className="min-w-full text-sm text-left text-gray-700">
        <thead className="bg-gray-100 font-semibold">
          <tr>
            {columns.map((col, index) => (
              <th key={`col-${index}`} className="px-4 py-2 border-b">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {row.map((value: any, j: number) => (
                <td key={`${i}-${j}`} className="px-4 py-2 border-b">
                  {String(value)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

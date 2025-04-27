import React from 'react';
import type { Table } from '@/types/query';

type Props = {
  data: Table;
};

export const QueryResultTable: React.FC<Props> = ({ data }) => {
  const { columns, rows } = data;

  if (!columns || !rows || !columns.length || !rows.length) return <p>No results found.</p>;

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 shadow">
      <table className="min-w-full text-sm text-left text-gray-700">
        <thead className="bg-gray-100 font-semibold">
          <tr>
            {columns.map((col) => (
              <th key={col} className="px-4 py-2 border-b">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col} className="px-4 py-2 border-b">
                  {String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
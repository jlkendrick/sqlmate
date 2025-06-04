"use client";

import { useEffect, useState } from "react";
// import {
//   getTables,
//   deleteUserTables,
//   getTableDataForExport,
// } from "@/lib/apiClient";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrashIcon, RefreshCw, PencilIcon, Download } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { Header } from "@/components/header";
import { DeleteTableResponse } from "@/types/http";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import { downloadTableAsCSV } from "@/utils/csv";
import { tableService } from "@/services/api";

interface UserTable {
  table_name: string;
  created_at: string;
}

export default function MyTablesPage() {
  const router = useRouter();
  const [tables, setTables] = useState<UserTable[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTables, setSelectedTables] = useState<string[]>([]);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState<string | null>(null);

  const fetchTables = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await tableService.getTables();
      setTables(data.tables || []);
      // Clear selections when refreshing
      setSelectedTables([]);

    } catch (err: any) {

      console.log(err);

      toast({
        title: "Error fetching tables",
        description: err.message || "Failed to load tables",
        variant: "destructive",
      });

      setError(err.message || "Failed to load tables");
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleSelection = (tableName: string) => {
    setSelectedTables((prev) =>
      prev.includes(tableName)
        ? prev.filter((name) => name !== tableName)
        : [...prev, tableName]
    );
  };

  const handleSelectAll = () => {
    if (selectedTables.length === tables.length) {
      setSelectedTables([]);
    } else {
      setSelectedTables(tables.map((table) => table.table_name));
    }
  };

  const handleDeleteTable = async (tableName: string) => {
    setDeleteLoading(true);
    try {
      const response = await tableService.deleteTables({ table_names: [tableName] });

      // Remove deleted table from the list
      setTables((prev) =>
        prev.filter((table) => table.table_name !== tableName)
      );
      // Remove from selected tables if it was selected
      setSelectedTables((prev) => prev.filter((name) => name !== tableName));
      toast({
        title: "Table deleted",
        description: `Successfully deleted table: ${tableName}`,
      });
    } catch (err: any) {
      setError(err.message || "Failed to delete table");
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedTables.length === 0) return;

    setDeleteLoading(true);
    try {
      const response = await tableService.deleteTables(
        { table_names: selectedTables }
      );

      if (response.success) {
        // Remove all deleted tables from the list
        setTables((prev) =>
          prev.filter((table) => !selectedTables.includes(table.table_name))
        );
        // Clear selections
        setSelectedTables([]);
        toast({
          title: "Tables deleted",
          description: `Successfully deleted ${response.deleted_tables.length} tables`,
        });
      } else {
        setError(`Failed to delete tables: ${response.message}`);
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage || "Failed to delete table");
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleEditTable = (tableName: string) => {
    // For now, we'll just navigate to a placeholder route
    router.push(`/edit-table/${tableName}`);
  };

  const handleDownloadCSV = async (tableName: string) => {
    setDownloadLoading(tableName);
    try {
      const tableData = await getTableDataForExport(tableName);
      downloadTableAsCSV(tableData, tableName);
      toast({
        title: "Download successful",
        description: `${tableName}.csv has been downloaded`,
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage || "Failed to download table");
      toast({
        title: "Download failed",
        description: errorMessage || "Failed to download table",
        variant: "destructive",
      });
    } finally {
      setDownloadLoading(null);
    }
  };

  useEffect(() => {
    fetchTables();
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="container mx-auto py-8 max-w-4xl flex-1">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">My Saved Tables</h1>
          <div className="flex gap-2">
            {selectedTables.length > 0 && (
              <Button
                variant="destructive"
                onClick={handleBulkDelete}
                disabled={deleteLoading}
                className="flex items-center gap-2"
              >
                <TrashIcon size={16} />
                Delete Selected ({selectedTables.length})
              </Button>
            )}
            <Button
              variant="outline"
              onClick={fetchTables}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <RefreshCw
                size={16}
                className={isLoading ? "animate-spin" : ""}
              />
              Refresh
            </Button>
          </div>
        </div>

        {error && (
          <Card className="p-4 mb-6 bg-red-50 border-red-200 text-red-700">
            <p>{error}</p>
          </Card>
        )}

        {isLoading ? (
          <div className="flex justify-center items-center p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : tables.length === 0 ? (
          <Card className="p-6 text-center bg-muted/20">
            <p className="text-muted-foreground mb-4">
              You don&apos;t have any saved tables yet.
            </p>
            <p className="text-sm">
              Run a query and click the &quot;Save Table&quot; button to save
              your results.
            </p>
          </Card>
        ) : (
          <div className="overflow-hidden rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted/50 border-b">
                  <th className="py-3 px-4 text-left font-medium w-10">
                    <Checkbox
                      checked={
                        selectedTables.length === tables.length &&
                        tables.length > 0
                      }
                      onCheckedChange={handleSelectAll}
                      aria-label="Select all tables"
                    />
                  </th>
                  <th className="py-3 px-4 text-left font-medium">
                    Table Name
                  </th>
                  <th className="py-3 px-4 text-left font-medium">Created</th>
                  <th className="py-3 px-4 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tables.map((table, index) => (
                  <tr
                    key={table.table_name}
                    className={`${
                      index % 2 === 0 ? "bg-background" : "bg-muted/20"
                    } hover:bg-muted/40 transition-colors`}
                  >
                    <td className="py-3 px-4">
                      <Checkbox
                        checked={selectedTables.includes(table.table_name)}
                        onCheckedChange={() =>
                          handleToggleSelection(table.table_name)
                        }
                        aria-label={`Select ${table.table_name}`}
                      />
                    </td>
                    <td className="py-3 px-4 font-medium">
                      {table.table_name}
                    </td>
                    <td className="py-3 px-4 text-muted-foreground">
                      {formatDistanceToNow(new Date(table.created_at), {
                        addSuffix: true,
                      })}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={() => handleEditTable(table.table_name)}
                        >
                          <PencilIcon size={16} className="text-blue-500" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={() => handleDeleteTable(table.table_name)}
                          disabled={deleteLoading}
                        >
                          <TrashIcon size={16} className="text-red-500" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={() => handleDownloadCSV(table.table_name)}
                          disabled={downloadLoading === table.table_name}
                        >
                          <Download size={16} className="text-green-500" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

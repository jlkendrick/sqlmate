"use client";

import React, { use, useEffect, useState } from "react";
import { Header } from "@/components/header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, RefreshCw, CheckCircle, AlertCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { getTableData, postTableUpdate } from "@/lib/apiClient";
import { QueryResultTable } from "@/components/queryResultTable";
import { TableUpdatePanel } from "@/components/tableUpdatePanel";
import { toast } from "@/components/ui/use-toast";
import type {
  Table,
  TableUpdateAttribute,
  TableUpdateConstraint,
  TableUpdateResponse,
} from "@/types/query";

interface EditTablePageProps {
  params: {
    tableName: string;
  };
}

export default function EditTablePage({ params }: EditTablePageProps) {
  // Access the tableName directly from params
  // @ts-ignore - Suppress Next.js params access warning
  const { tableName } = use(params);

  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [tableData, setTableData] = useState<Table | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [updateResult, setUpdateResult] = useState<{
    success: boolean;
    message: string;
    rowsAffected?: number;
  } | null>(null);

  // Transform columns from tableData to the format expected by TableUpdatePanel
  const columns = tableData
    ? tableData.columns.map((col) => ({ name: col, type: "" }))
    : [];

  const fetchTableData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTableData(tableName);
      setTableData(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch table data");

      // Handle unauthorized errors
      if (
        err.message?.includes("401") ||
        err.message?.includes("unauthorized")
      ) {
        router.push("/login");
        return;
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateSubmit = async (
    updates: TableUpdateAttribute[],
    constraints: TableUpdateConstraint[]
  ) => {
    setIsSubmitting(true);
    setUpdateResult(null);
    setError(null);

    try {
      // Create the update request payload
      const updateData = {
        table: tableName,
        updates,
        constraints,
      };

      // Send the update request to the backend
      const result = await postTableUpdate(updateData);

      setUpdateResult({
        success: result.success,
        message: result.message,
        rowsAffected: result.rows_affected,
      });

      // Show success toast
      toast({
        title: "Update successful",
        description: `${result.rows_affected || 0} row(s) affected`,
        variant: "default",
      });

      // Refresh the table data to show the updated data
      fetchTableData();
    } catch (err: any) {
      console.error("Update failed:", err);
      setError(err.message || "Failed to update table");

      // Show error toast
      toast({
        title: "Update failed",
        description: err.message || "Failed to update table",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    fetchTableData();
  }, [tableName]);

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="container mx-auto py-8 max-w-4xl flex-1">
        <div className="flex items-center mb-6">
          <Button
            variant="ghost"
            className="mr-4"
            onClick={() => router.back()}
          >
            <ArrowLeft size={16} className="mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Edit Table: {tableName}</h1>

          <Button
            variant="outline"
            className="ml-auto"
            onClick={fetchTableData}
            disabled={isLoading}
          >
            <RefreshCw
              size={16}
              className={`mr-2 ${isLoading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>

        {error && (
          <Card className="p-4 mb-6 bg-red-50 border-red-200 text-red-700">
            <div className="flex items-center">
              <AlertCircle size={16} className="mr-2" />
              <p>{error}</p>
            </div>
          </Card>
        )}

        {updateResult && updateResult.success && (
          <Card className="p-4 mb-6 bg-green-50 border-green-200 text-green-700">
            <div className="flex items-center">
              <CheckCircle size={16} className="mr-2" />
              <p>
                {updateResult.message}
                {updateResult.rowsAffected !== undefined &&
                  ` (${updateResult.rowsAffected} row${
                    updateResult.rowsAffected !== 1 ? "s" : ""
                  } affected)`}
              </p>
            </div>
          </Card>
        )}

        {/* Table Update Panel */}
        {!isLoading && tableData && (
          <TableUpdatePanel
            tableName={tableName}
            columns={columns}
            onSubmit={handleUpdateSubmit}
            isSubmitting={isSubmitting}
          />
        )}

        {isLoading ? (
          <div className="flex justify-center items-center p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="space-y-6">
            <Card className="p-6">
              {tableData ? (
                <QueryResultTable data={tableData} />
              ) : (
                <p className="text-center text-muted-foreground">
                  No table data available
                </p>
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

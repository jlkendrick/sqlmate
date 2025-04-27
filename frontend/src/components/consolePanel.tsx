import { useState } from "react";
import { Button } from "@/components/ui/button";
import { QueryResultTable } from "@/components/queryResultTable";
import type { Table, SaveTableRequest } from "@/types/query";
import { useRouter } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { SaveIcon } from "lucide-react";
import { postUserTable } from "@/lib/apiClient";

export function ConsolePanel({
  consoleOutput,
  queryOutput,
}: {
  consoleOutput: Table | null;
  queryOutput: string | null;
}) {
  const [activeTab, setActiveTab] = useState<"results" | "query">("results");
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [tableName, setTableName] = useState("");
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const router = useRouter();

  const handleSaveTable = async () => {
    if (!queryOutput) {
      setSaveError("No query results to save");
      return;
    }

    // Validate tablename
    if (!tableName.trim()) {
      setSaveError("Please enter a valid table name");
      return;
    }

    // Reset states
    setSaveError(null);
    setSaveSuccess(null);
    setIsSaving(true);

    try {
      // Create the request data
      const saveTableData: SaveTableRequest = {
        table_name: tableName.trim(),
        query: queryOutput,
      };

      // Send the request to save the table
      await postUserTable(saveTableData);

      // Success
      setSaveSuccess(`Table "${tableName}" saved successfully!`);
      setTableName("");

      // Close dialog after a delay
      setTimeout(() => {
        setShowSaveDialog(false);
        setSaveSuccess(null);
      }, 1500);
    } catch (error: any) {
      // Handle auth errors - redirect to login if not authenticated
      if (
        error.message?.includes("401") ||
        error.message?.includes("unauthorized")
      ) {
        router.push("/login");
        return;
      }

      // Set error message for other errors
      setSaveError(error.message || "Failed to save table");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="h-full flex flex-col border-t border-console-border bg-console">
      <div className="flex items-center justify-between px-4 h-10">
        <div className="flex items-center space-x-4">
          <Button
            variant="secondary"
            size="sm"
            className={`text-sm px-3 py-1 h-auto ${
              activeTab === "query" ? "bg-background" : ""
            }`}
            onClick={() => setActiveTab("results")}
          >
            Results
          </Button>
          <Button
            variant="secondary"
            size="sm"
            className={`text-sm px-3 py-1 h-auto ${
              activeTab === "results" ? "bg-background" : ""
            }`}
            onClick={() => setActiveTab("query")}
          >
            Query
          </Button>
        </div>

        {/* Save Table Button */}
        <Button
          variant="outline"
          size="sm"
          className="text-sm px-3 py-1 h-auto flex items-center gap-1"
          onClick={() => setShowSaveDialog(true)}
          disabled={!consoleOutput || !queryOutput}
        >
          <SaveIcon size={14} /> Save Table
        </Button>
      </div>
      <div className="flex-1 p-4 overflow-auto">
        {activeTab === "results" ? (
          <div className="h-full font-mono text-sm p-3 bg-background rounded border border-border">
            {consoleOutput ? (
              <QueryResultTable data={consoleOutput} />
            ) : (
              <p>No results to display</p>
            )}
          </div>
        ) : (
          <div className="font-mono text-sm p-3 bg-background rounded border border-border h-full">
            {queryOutput ? (
              <pre className="whitespace-pre-wrap break-words">
                {queryOutput}
              </pre>
            ) : (
              <p>No query to display</p>
            )}
          </div>
        )}
      </div>

      {/* Save Table Dialog */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Save Table</DialogTitle>
            <DialogDescription>
              Enter a name for your table. This table will be saved to your
              account and can be accessed later.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label htmlFor="tableName" className="text-sm font-medium">
                Table Name
              </label>
              <Input
                id="tableName"
                placeholder="my_custom_table"
                value={tableName}
                onChange={(e) => {
                  setTableName(e.target.value);
                  setSaveError(null);
                }}
                className={saveError ? "border-red-500" : ""}
              />
              {saveError && <p className="text-sm text-red-500">{saveError}</p>}
              {saveSuccess && (
                <p className="text-sm text-green-500">{saveSuccess}</p>
              )}
            </div>
          </div>

          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" disabled={isSaving}>
                Cancel
              </Button>
            </DialogClose>
            <Button
              onClick={handleSaveTable}
              disabled={isSaving || !tableName.trim()}
            >
              {isSaving ? "Saving..." : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

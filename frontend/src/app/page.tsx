"use client";
import { useState } from "react";
import type { Table } from "@/types/common";
import { Header } from "@/components/header";
import { TablePanel } from "@/components/tablePanel";
import { StudioCanvas } from "@/components/studioCanvas";
import { ConsolePanel } from "@/components/consolePanel";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
} from "@dnd-kit/core";
import { TableItem } from "@/components/tablePanel";
import { Card } from "@/components/ui/card";

export default function Home() {
  const [consoleOutput, setConsoleOutput] = useState<Table | null>(null);
  const [queryOutput, setQueryOutput] = useState<string | null>(null);
  const [droppedTables, setDroppedTables] = useState<TableItem[]>([]);
  const [activeTable, setActiveTable] = useState<TableItem | null>(null);

  const handleDragStart = (event: DragStartEvent) => {
    // Set the active table data for the overlay
    if (event.active.data.current) {
      setActiveTable(event.active.data.current as TableItem);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    // Reset active table
    setActiveTable(null);

    if (over && over.id === "studio-dropzone") {
      // Get the table data from the dragged item
      const tableData = active.data.current as TableItem;

      // Check if table already exists in droppedTables
      const tableExists = droppedTables.some(
        (table) => table.id === tableData.id
      );

      if (!tableExists) {
        setDroppedTables((prev) => [...prev, tableData]);
      }
    }
  };

  // Drag overlay table preview component
  const DragPreview = ({ table }: { table: TableItem }) => {
    return (
      <Card className="p-3 bg-background shadow-md border-2 border-primary w-64">
        <div className="font-medium text-sm">{table.name}</div>
        <div className="mt-2 text-xs text-muted-foreground">
          {table.columns.length} columns
        </div>
      </Card>
    );
  };

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="flex flex-col h-screen w-full">
        <Header />
        <div className="flex h-full relative">
          <TablePanel />
          <ResizablePanelGroup direction="horizontal" className="flex-1">
            <ResizablePanel>
              <StudioCanvas
                setConsoleOutput={setConsoleOutput}
                setQueryOutput={setQueryOutput}
                droppedTables={droppedTables}
                setDroppedTables={setDroppedTables}
              />
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={30} minSize={10}>
              <ConsolePanel
                consoleOutput={consoleOutput}
                queryOutput={queryOutput}
              />
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>

        {/* Drag overlay for table preview */}
        <DragOverlay dropAnimation={null}>
          {activeTable ? <DragPreview table={activeTable} /> : null}
        </DragOverlay>
      </div>
    </DndContext>
  );
}

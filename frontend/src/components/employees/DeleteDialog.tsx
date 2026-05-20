/**
 * Delete confirmation dialog — confirms soft-delete with toast feedback.
 */

"use client";

import React from "react";
import { Dialog, Button, toast } from "@/components/ui";
import { del } from "@/lib/api";
import type { Employee } from "@/lib/validators";

interface Props {
  employee: Employee | null;
  open: boolean;
  onClose: () => void;
  onDeleted: () => void;
}

export default function DeleteDialog({
  employee,
  open,
  onClose,
  onDeleted,
}: Props) {
  const [isDeleting, setIsDeleting] = React.useState(false);

  const handleConfirm = async () => {
    if (!employee) return;
    setIsDeleting(true);
    try {
      await del(`/employees/${employee.id}`);
      toast(`${employee.full_name} has been deactivated`, "success");
      onDeleted();
      onClose();
    } catch (err: any) {
      toast(err.message || "Failed to delete employee", "error");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-white">
            Deactivate Employee
          </h3>
          <p className="mt-2 text-sm text-slate-400">
            Are you sure you want to deactivate{" "}
            <span className="font-medium text-white">
              {employee?.full_name}
            </span>
            ? This will soft-delete the employee record. They can be
            reactivated later.
          </p>
        </div>
        <div className="flex items-center justify-end gap-3">
          <Button variant="outline" onClick={onClose} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? "Deactivating..." : "Deactivate"}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}

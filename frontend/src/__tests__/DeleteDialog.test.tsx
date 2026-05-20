/**
 * React Testing Library tests for DeleteDialog.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import DeleteDialog from "@/components/employees/DeleteDialog";

// Mock the API module
vi.mock("@/lib/api", () => ({
  del: vi.fn(),
}));

// Mock the toast
vi.mock("@/components/ui", async () => {
  const actual = await vi.importActual("@/components/ui");
  return {
    ...actual,
    toast: vi.fn(),
  };
});

const mockEmployee = {
  id: 42,
  full_name: "Jane Doe",
  email: "jane@test.com",
  job_title_id: 1,
  department_id: 1,
  job_title: "Engineer",
  department: "Engineering",
  country: "US",
  salary: 100000,
  currency: "USD",
  employment_type: "full-time",
  hire_date: "2024-01-15",
  is_active: true,
  created_at: "2024-01-15T00:00:00Z",
  updated_at: "2024-01-15T00:00:00Z",
};

describe("DeleteDialog", () => {
  it("does not render when open is false", () => {
    render(
      <DeleteDialog
        employee={mockEmployee}
        open={false}
        onClose={vi.fn()}
        onDeleted={vi.fn()}
      />
    );
    expect(screen.queryByText("Deactivate Employee")).not.toBeInTheDocument();
  });

  it("renders dialog when open is true", () => {
    render(
      <DeleteDialog
        employee={mockEmployee}
        open={true}
        onClose={vi.fn()}
        onDeleted={vi.fn()}
      />
    );
    expect(screen.getByText("Deactivate Employee")).toBeInTheDocument();
    expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
  });

  it("calls onClose when Cancel is clicked (API NOT called)", async () => {
    const onClose = vi.fn();
    const onDeleted = vi.fn();
    const { del } = await import("@/lib/api");

    render(
      <DeleteDialog
        employee={mockEmployee}
        open={true}
        onClose={onClose}
        onDeleted={onDeleted}
      />
    );

    await userEvent.click(screen.getByText("Cancel"));
    expect(onClose).toHaveBeenCalled();
    expect(del).not.toHaveBeenCalled();
    expect(onDeleted).not.toHaveBeenCalled();
  });

  it("calls API on confirm and triggers onDeleted", async () => {
    const onClose = vi.fn();
    const onDeleted = vi.fn();
    const { del } = await import("@/lib/api");
    (del as ReturnType<typeof vi.fn>).mockResolvedValue({});

    render(
      <DeleteDialog
        employee={mockEmployee}
        open={true}
        onClose={onClose}
        onDeleted={onDeleted}
      />
    );

    await userEvent.click(screen.getByText("Deactivate"));

    await waitFor(() => {
      expect(del).toHaveBeenCalledWith("/employees/42");
      expect(onDeleted).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });
});

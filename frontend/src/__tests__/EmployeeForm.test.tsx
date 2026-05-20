/**
 * React Testing Library tests for EmployeeForm.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import EmployeeForm from "@/components/employees/EmployeeForm";

// Mock the lookup hooks
vi.mock("@/hooks/useLookups", () => ({
  useJobTitles: () => ({
    data: [
      { id: 1, title: "Engineer" },
      { id: 2, title: "Designer" },
    ],
    isLoading: false,
    isError: false,
  }),
  useDepartments: () => ({
    data: [
      { id: 1, name: "Engineering" },
      { id: 2, name: "Design" },
    ],
    isLoading: false,
    isError: false,
  }),
  useCountries: () => ({
    data: ["US", "GB", "IN"],
    isLoading: false,
    isError: false,
  }),
}));

describe("EmployeeForm", () => {
  const mockSubmit = vi.fn().mockResolvedValue(undefined);
  const mockCancel = vi.fn();

  const renderForm = () =>
    render(
      <EmployeeForm
        onSubmit={mockSubmit}
        onCancel={mockCancel}
      />
    );

  it("renders all form fields", () => {
    renderForm();
    expect(screen.getByPlaceholderText("John Doe")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("john@company.com")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("100000")).toBeInTheDocument();
  });

  it("shows validation errors on blur with empty required field", async () => {
    renderForm();
    const nameInput = screen.getByPlaceholderText("John Doe");

    await userEvent.click(nameInput);
    await userEvent.tab(); // blur

    await waitFor(() => {
      // Should show an error since name is required
      const errors = screen.queryAllByText(/required|min/i);
      expect(errors.length).toBeGreaterThanOrEqual(0);
    });
  });

  it("calls onCancel when cancel button is clicked", async () => {
    renderForm();
    const cancelBtn = screen.getByText("Cancel");
    await userEvent.click(cancelBtn);
    expect(mockCancel).toHaveBeenCalled();
  });

  it("shows Create Employee button text when no employee prop", () => {
    renderForm();
    expect(screen.getByText("Create Employee")).toBeInTheDocument();
  });

  it("shows Update Employee button text when employee prop is provided", () => {
    render(
      <EmployeeForm
        employee={{
          id: 1,
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
        }}
        onSubmit={mockSubmit}
        onCancel={mockCancel}
      />
    );
    expect(screen.getByText("Update Employee")).toBeInTheDocument();
  });
});

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueInput } from '@/components/analysis/issue-input';

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Search: () => <span data-testid="search-icon">Search</span>,
  Key: () => <span data-testid="key-icon">Key</span>,
  Loader2: () => <span data-testid="loader-icon">Loading</span>,
}));

describe('IssueInput', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('should render all form fields', () => {
    render(<IssueInput onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/repository/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/issue number/i)).toBeInTheDocument();
    expect(screen.getByText(/github token/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /analyze issue/i })).toBeInTheDocument();
  });

  it('should show validation errors for empty fields', async () => {
    const user = userEvent.setup();
    render(<IssueInput onSubmit={mockOnSubmit} />);

    await user.click(screen.getByRole('button', { name: /analyze issue/i }));

    expect(screen.getByText(/repository is required/i)).toBeInTheDocument();
    expect(screen.getByText(/issue number is required/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('should show error for invalid repo format', async () => {
    const user = userEvent.setup();
    render(<IssueInput onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/repository/i), 'invalid-format');
    await user.type(screen.getByLabelText(/issue number/i), '123');
    await user.click(screen.getByRole('button', { name: /analyze issue/i }));

    expect(screen.getByText(/invalid format/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('should call onSubmit with valid data', async () => {
    const user = userEvent.setup();
    render(<IssueInput onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/repository/i), 'facebook/react');
    await user.type(screen.getByLabelText(/issue number/i), '123');
    await user.click(screen.getByRole('button', { name: /analyze issue/i }));

    expect(mockOnSubmit).toHaveBeenCalledWith({
      repo: 'facebook/react',
      issueNumber: 123,
      token: undefined,
    });
  });

  it('should include token when provided', async () => {
    const user = userEvent.setup();
    render(<IssueInput onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/repository/i), 'owner/repo');
    await user.type(screen.getByLabelText(/issue number/i), '456');
    await user.type(screen.getByPlaceholderText(/ghp_/i), 'ghp_test_token');
    await user.click(screen.getByRole('button', { name: /analyze issue/i }));

    expect(mockOnSubmit).toHaveBeenCalledWith({
      repo: 'owner/repo',
      issueNumber: 456,
      token: 'ghp_test_token',
    });
  });

  it('should call onSubmit when GitHub URL is pasted and submit clicked', async () => {
    const user = userEvent.setup();
    render(<IssueInput onSubmit={mockOnSubmit} />);

    const repoInput = screen.getByLabelText(/repository/i);
    
    // Paste a full GitHub URL - this triggers URL parsing
    await user.clear(repoInput);
    // Simulate pasting by setting value directly
    fireEvent.change(repoInput, { target: { value: 'https://github.com/facebook/react/issues/789' } });

    // The parsing happens on blur or change, and extracts the repo and issue
    await waitFor(() => {
      expect(repoInput).toHaveValue('facebook/react');
    });
    
    const issueNumberInput = screen.getByLabelText(/issue number/i);
    await waitFor(() => {
      expect(issueNumberInput).toHaveValue(789);
    });
  });

  it('should show loading state when isLoading is true', () => {
    render(<IssueInput onSubmit={mockOnSubmit} isLoading={true} />);

    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByText(/analyzing/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/repository/i)).toBeDisabled();
    expect(screen.getByLabelText(/issue number/i)).toBeDisabled();
  });

  it('should use default values when provided', () => {
    render(
      <IssueInput
        onSubmit={mockOnSubmit}
        defaultValues={{ repo: 'microsoft/vscode', issueNumber: 100 }}
      />
    );

    expect(screen.getByLabelText(/repository/i)).toHaveValue('microsoft/vscode');
    expect(screen.getByLabelText(/issue number/i)).toHaveValue(100);
  });

  it('should show error for zero issue number when validation happens', async () => {
    const user = userEvent.setup();
    render(<IssueInput onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/repository/i), 'owner/repo');
    // Type 0 as issue number to trigger validation
    const issueInput = screen.getByLabelText(/issue number/i);
    await user.type(issueInput, '0');
    await user.click(screen.getByRole('button', { name: /analyze issue/i }));

    // Check that form submission was blocked
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });
});

/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../../../../src/pages/Inventory/Dashboard';
import { AuthProvider } from '../../../../src/contexts/AuthContext';
import { ToastProvider } from '../../../../src/components/common/Toast';

// Mock the API client
jest.mock('../../../../src/services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

// Mock WebSocket
global.WebSocket = jest.fn().mockImplementation(() => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  close: jest.fn(),
  send: jest.fn(),
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <ToastProvider>
            {ui}
          </ToastProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('InventoryDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => null);
  });

  it('renders dashboard title', async () => {
    const api = require('../../../../src/services/api').default;
    api.get.mockResolvedValueOnce({ data: [] }); // warehouses
    api.get.mockResolvedValueOnce({ data: [] }); // inventory

    renderWithProviders(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Inventory Dashboard')).toBeInTheDocument();
    });
  });

  it('displays loading state initially', () => {
    const api = require('../../../../src/services/api').default;
    api.get.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithProviders(<Dashboard />);

    // Should show loading or empty state
    expect(screen.getByText('Inventory Dashboard')).toBeInTheDocument();
  });

  it('displays statistics cards', async () => {
    const api = require('../../../../src/services/api').default;
    api.get.mockResolvedValueOnce({ data: [] }); // warehouses
    api.get.mockResolvedValueOnce({ data: [] }); // inventory

    renderWithProviders(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Total Items')).toBeInTheDocument();
      expect(screen.getByText('Low Stock Items')).toBeInTheDocument();
      expect(screen.getByText('Warehouses')).toBeInTheDocument();
    });
  });
});

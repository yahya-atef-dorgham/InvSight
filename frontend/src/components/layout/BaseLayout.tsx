import React from 'react';
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ToastProvider } from '../common/Toast';
import Dashboard from '../../pages/Inventory/Dashboard';
import Movements from '../../pages/Inventory/Movements';
import RecommendationsDashboard from '../../pages/Recommendations/Dashboard';
import PurchaseOrdersList from '../../pages/PurchaseOrders/List';
import VoiceAssistant from '../../pages/Voice/Assistant';
import './BaseLayout.css';

const BaseLayout: React.FC = () => {
  const { isAuthenticated, isLoading, logout, user } = useAuth();
  const navigate = useNavigate();

  // Redirect to login if not authenticated
  if (!isLoading && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <ToastProvider>
      <div className="base-layout">
        <header className="app-header">
          <div className="header-content">
            <h1 className="app-title">Inventory Management</h1>
            <nav className="app-nav">
              <Link to="/inventory" className="nav-link">Inventory</Link>
              <Link to="/movements" className="nav-link">Movements</Link>
              <Link to="/recommendations" className="nav-link">Recommendations</Link>
              <Link to="/purchase-orders" className="nav-link">Purchase Orders</Link>
              <Link to="/voice" className="nav-link">Voice Assistant</Link>
              <Link to="/products" className="nav-link">Products</Link>
              <Link to="/warehouses" className="nav-link">Warehouses</Link>
            </nav>
            <div className="user-section">
              {user && (
                <span className="user-info">
                  {user.user_id} ({user.tenant_id})
                </span>
              )}
              <button onClick={handleLogout} className="logout-button">
                Logout
              </button>
            </div>
          </div>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/inventory" element={<Dashboard />} />
            <Route path="/movements" element={<Movements />} />
            <Route path="/recommendations" element={<RecommendationsDashboard />} />
            <Route path="/purchase-orders" element={<PurchaseOrdersList />} />
            <Route path="/voice" element={<VoiceAssistant />} />
            <Route path="/products" element={<div className="page-content"><h2>Products</h2><p>Products page coming soon...</p></div>} />
            <Route path="/warehouses" element={<div className="page-content"><h2>Warehouses</h2><p>Warehouses page coming soon...</p></div>} />
            <Route path="*" element={<Navigate to="/inventory" replace />} />
          </Routes>
        </main>
      </div>
    </ToastProvider>
  );
};

export default BaseLayout;

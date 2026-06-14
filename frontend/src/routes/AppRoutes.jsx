import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import Groups from '../pages/Groups';
import Balances from '../pages/Balances';
import Expenses from '../pages/Expenses';
import ImportCSV from '../pages/ImportCSV';

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/groups" element={<Groups />} />
        <Route path="/balances" element={<Balances />} />
        <Route path="/expenses" element={<Expenses />} />
        <Route path="/import" element={<ImportCSV />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
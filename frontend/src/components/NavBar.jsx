import { Link, useNavigate } from 'react-router-dom';

function NavBar() {
  const navigate = useNavigate();
  const token = localStorage.getItem('authToken');

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    navigate('/');
  };

  return (
    <nav style={{ padding: '12px 16px', borderBottom: '1px solid #ddd', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Link to="/dashboard" style={{ marginRight: '16px', fontWeight: 600 }}>Dashboard</Link>
        <Link to="/groups" style={{ marginRight: '12px' }}>Groups</Link>
        <Link to="/balances" style={{ marginRight: '12px' }}>Balances</Link>
        <Link to="/expenses" style={{ marginRight: '12px' }}>Expenses</Link>
        <Link to="/import" style={{ marginLeft: 8 }}>Import</Link>
      </div>

      <div>
        {token ? (
          <button onClick={handleLogout} style={{ padding: '6px 10px' }}>Logout</button>
        ) : (
          <Link to="/">Login</Link>
        )}
      </div>
    </nav>
  );
}

export default NavBar;

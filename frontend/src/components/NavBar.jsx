import { Link } from 'react-router-dom';

function NavBar() {
  return (
    <nav style={{ padding: '16px', borderBottom: '1px solid #ddd' }}>
      <Link to="/dashboard" style={{ marginRight: '16px' }}>Dashboard</Link>
      <Link to="/groups" style={{ marginRight: '16px' }}>Groups</Link>
      <Link to="/balances" style={{ marginRight: '16px' }}>Balances</Link>
      <Link to="/expenses" style={{ marginRight: '16px' }}>Expenses</Link>
      <Link to="/import" style={{ marginRight: '16px' }}>Import CSV</Link>
    </nav>
  );
}

export default NavBar;

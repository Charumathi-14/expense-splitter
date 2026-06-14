import NavBar from './NavBar';

function Layout({ children }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <NavBar />
      <main style={{ flex: 1, padding: 24 }}>{children}</main>
      <footer style={{ padding: 12, textAlign: 'center', color: '#888' }}>Expense Splitter — local</footer>
    </div>
  );
}

export default Layout;

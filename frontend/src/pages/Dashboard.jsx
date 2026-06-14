import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import NavBar from '../components/NavBar';

function Dashboard() {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [balance, setBalance] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups/');
      setGroups(response.data);
    } catch (err) {
      navigate('/');
    }
  };

  const handleSelectGroup = async (group) => {
    try {
      setError('');
      setSelectedGroup(group);
      const response = await api.get(`/groups/${group.id}/balance/`);
      setBalance(response.data);
    } catch (err) {
      setError('Unable to load group balance.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    navigate('/');
  };

  return (
    <div>
      <NavBar />
      <div style={{ padding: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Dashboard</h1>
            <p>Choose a group to review balances and settlement suggestions.</p>
          </div>
          <button onClick={handleLogout} style={{ padding: '8px 16px' }}>
            Logout
          </button>
        </div>

        {error && <p style={{ color: 'red' }}>{error}</p>}

        <section style={{ display: 'flex', gap: 24, marginTop: 24 }}>
          <div style={{ flex: 1, minWidth: 280, border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
            <h2>Groups</h2>
            {groups.length === 0 ? (
              <p>No groups found yet. Use the Import page to load CSV data.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {groups.map((group) => (
                  <li key={group.id} style={{ marginBottom: 12 }}>
                    <button
                      style={{ width: '100%', padding: 10, textAlign: 'left' }}
                      onClick={() => handleSelectGroup(group)}
                    >
                      {group.name}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div style={{ flex: 2, minWidth: 320, border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
            {selectedGroup ? (
              <div>
                <h2>{selectedGroup.name} balance</h2>
                {balance ? (
                  <>
                    <div>
                      <h3>Member balances</h3>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left', padding: 8 }}>User</th>
                            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'right', padding: 8 }}>Amount</th>
                          </tr>
                        </thead>
                        <tbody>
                          {balance.balances.map((user) => (
                            <tr key={user.user_id}>
                              <td style={{ padding: 8 }}>{user.user_name || `User ${user.user_id}`}</td>
                              <td style={{ padding: 8, textAlign: 'right' }}>{user.balance}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div style={{ marginTop: 24 }}>
                      <h3>Suggested settlements</h3>
                      {balance.recommended_settlements.length === 0 ? (
                        <p>No settlements needed.</p>
                      ) : (
                        <ul>
                          {balance.recommended_settlements.map((settlement, idx) => (
                            <li key={idx}>
                              User {settlement.from_user_id} pays User {settlement.to_user_id} ₹{settlement.amount}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </>
                ) : (
                  <p>Select a group to load the balance report.</p>
                )}
              </div>
            ) : (
              <p>Select a group from the left to get started.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;

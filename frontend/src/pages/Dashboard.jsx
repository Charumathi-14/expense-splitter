import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/Layout';

function Dashboard() {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [balance, setBalance] = useState(null);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState({ groups: 0, expenses: 0, settlements: 0 });
  const [loadingSummary, setLoadingSummary] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchGroups();
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    setLoadingSummary(true);
    try {
      const [gRes, eRes, sRes] = await Promise.all([
        api.get('/groups/'),
        api.get('/expenses/'),
        api.get('/settlements/'),
      ]);
      setSummary({ groups: gRes.data.length || 0, expenses: eRes.data.length || 0, settlements: sRes.data.length || 0 });
    } catch (err) {
      // ignore, summary optional
    } finally {
      setLoadingSummary(false);
    }
  };

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

  return (
    <Layout>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Dashboard</h1>
            <p>Overview of your groups and balances.</p>
          </div>
        </div>

        {loadingSummary ? (
          <p>Loading summary...</p>
        ) : (
          <div style={{ display: 'flex', gap: 16, marginTop: 16 }}>
            <div style={{ flex: 1, padding: 16, border: '1px solid var(--border)', borderRadius: 8 }}>
              <h3>Groups</h3>
              <p style={{ fontSize: 24, margin: 8 }}>{summary.groups}</p>
            </div>
            <div style={{ flex: 1, padding: 16, border: '1px solid var(--border)', borderRadius: 8 }}>
              <h3>Expenses</h3>
              <p style={{ fontSize: 24, margin: 8 }}>{summary.expenses}</p>
            </div>
            <div style={{ flex: 1, padding: 16, border: '1px solid var(--border)', borderRadius: 8 }}>
              <h3>Settlements</h3>
              <p style={{ fontSize: 24, margin: 8 }}>{summary.settlements}</p>
            </div>
          </div>
        )}

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
    </Layout>
  );
}

export default Dashboard;

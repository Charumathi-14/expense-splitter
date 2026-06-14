import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/Layout';

function Balances() {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [balance, setBalance] = useState(null);
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

  const fetchBalance = async (group) => {
    try {
      setSelectedGroup(group);
      const response = await api.get(`/groups/${group.id}/balance/`);
      setBalance(response.data);
    } catch {
      setBalance(null);
    }
  };

  return (
    <Layout>
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        <h1>Balances</h1>
        <div style={{ display: 'flex', gap: 24 }}>
          <div style={{ width: 260, border: '1px solid #ddd', padding: 16, borderRadius: 8 }}>
            <h2>Groups</h2>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {groups.map((group) => (
                <li key={group.id} style={{ marginBottom: 8 }}>
                  <button style={{ width: '100%', padding: 8, textAlign: 'left' }} onClick={() => fetchBalance(group)}>
                    {group.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <div style={{ flex: 1, border: '1px solid #ddd', padding: 16, borderRadius: 8 }}>
            {selectedGroup ? (
              <>
                <h2>{selectedGroup.name}</h2>
                <p>Balance summary for selected group.</p>
                {balance ? (
                  <div>
                    <h3>Member balances</h3>
                    <ul>
                      {balance.balances.map((item) => (
                        <li key={item.user_id}>{item.user_name || item.user_id}: ₹{item.balance}</li>
                      ))}
                    </ul>
                    <h3>Suggested payments</h3>
                    <ul>
                      {balance.recommended_settlements.length === 0 ? (
                        <li>No suggested settlements.</li>
                      ) : (
                        balance.recommended_settlements.map((settlement, idx) => (
                          <li key={idx}>
                            User {settlement.from_user_id} pays User {settlement.to_user_id}: ₹{settlement.amount}
                          </li>
                        ))
                      )}
                    </ul>
                  </div>
                ) : (
                  <p>Select a group to load its balance details.</p>
                )}
              </>
            ) : (
              <p>Select a group from the left to view balances.</p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Balances;

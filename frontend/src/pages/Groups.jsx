import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import NavBar from '../components/NavBar';

function Groups() {
  const [groups, setGroups] = useState([]);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const response = await api.get('/groups/');
      setGroups(response.data);
    } catch (err) {
      navigate('/');
    }
  };

  const createGroup = async () => {
    if (!name.trim()) {
      setMessage('Group name is required.');
      return;
    }
    try {
      const response = await api.post('/groups/', { name, description: '' });
      setGroups((prev) => [...prev, response.data]);
      setName('');
      setMessage('Group created successfully.');
    } catch (err) {
      setMessage('Failed to create group.');
    }
  };

  return (
    <div>
      <NavBar />
      <div style={{ padding: 24 }}>
        <h1>Groups</h1>
        <div style={{ marginBottom: 24 }}>
          <input
            style={{ padding: 10, width: 240, marginRight: 8 }}
            type="text"
            placeholder="New group name"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <button onClick={createGroup} style={{ padding: '10px 16px' }}>
            Create group
          </button>
        </div>
        {message && <p>{message}</p>}
        <div>
          <h2>Existing groups</h2>
          {groups.length === 0 ? (
            <p>No groups found.</p>
          ) : (
            <ul>
              {groups.map((group) => (
                <li key={group.id} style={{ marginBottom: 8 }}>
                  {group.name}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default Groups;

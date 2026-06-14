import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleLogin = async () => {
    setMessage('');
    try {
      const response = await api.post('/accounts/login/', {
        email,
        password,
      });

      if (response.data?.token) {
        localStorage.setItem('authToken', response.data.token);
        navigate('/dashboard');
      }
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Login failed.');
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: '64px auto', padding: 24, border: '1px solid #ddd', borderRadius: 8 }}>
      <h1>Expense Splitter</h1>
      <div style={{ marginBottom: 16 }}>
        <input
          style={{ width: '100%', padding: 10, boxSizing: 'border-box' }}
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
      </div>
      <div style={{ marginBottom: 16 }}>
        <input
          style={{ width: '100%', padding: 10, boxSizing: 'border-box' }}
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </div>
      <button style={{ width: '100%', padding: 10 }} onClick={handleLogin}>Login</button>
      {message && <p style={{ color: 'red', marginTop: 16 }}>{message}</p>}
    </div>
  );
}

export default Login;
import React, { useState } from 'react';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState(null); //holds {name, role}
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const res = await fetch('https://software-engineering-project-h2hj.onrender.com/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
        credentials: 'include',
      });

      const data = await res.json();

      if (res.ok && data.success) {
        setUser({ name: data.name, role: data.role });
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleLogout = async () => {
    await fetch('https://software-engineering-project-h2hj.onrender.com/logout', {credentials: 'include' });
    setUser(null);
    setUsername('');
    setPassword('');
  };

  if (user) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>Welcome, {user.name} ({user.role})</h2>
        {user.role === 'doctor' && <p>You are logged in as a doctor. Here you can view patients, assign treatments, etc.</p>}
        {user.role === 'patient' && <p>You are logged in as a patient. Here you can view your medical info and treatment plans.</p>}
        <button onClick={handleLogout}>Logout</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Login</h2>
      {error && <p style={{ color: 'red'}}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
        /><br /><br />
        <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        /><br /><br />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default App;
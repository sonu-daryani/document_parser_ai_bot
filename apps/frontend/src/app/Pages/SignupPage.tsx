import React, { useState } from 'react';
import { api } from '../lib/api';
import { Link, useNavigate } from 'react-router-dom';

export default function SignupPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;
    setLoading(true);
    setError(null);
    try {
      await api.post('/api/auth/signup', { username, password });
      navigate('/');
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <form onSubmit={onSubmit} className="w-full max-w-sm bg-white p-6 rounded-xl shadow">
        <h1 className="text-2xl font-bold mb-4">Sign up</h1>
        {error && <div className="text-red-600 text-sm mb-3">{error}</div>}
        <label className="block mb-2 text-sm font-medium">Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} className="w-full mb-4 border rounded px-3 py-2" />
        <label className="block mb-2 text-sm font-medium">Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full mb-6 border rounded px-3 py-2" />
        <button disabled={loading} className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50">{loading ? 'Creating...' : 'Create account'}</button>
        <div className="mt-4 text-sm">
          Already have an account? <Link className="text-blue-600" to="/login">Login</Link>
        </div>
      </form>
    </div>
  );
}



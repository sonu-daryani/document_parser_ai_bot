// Uncomment this line to use CSS modules
// import styles from './app.module.css';

import { Route, Routes } from 'react-router-dom';
import { Suspense, lazy, useEffect, useState } from 'react';
import { api } from './lib/api';

const LandingPage = lazy(() => import('./Pages/LandingPage'));
const LoginPage = lazy(() => import('./Pages/LoginPage'));
const SignupPage = lazy(() => import('./Pages/SignupPage'));

export function App() {
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuthed, setIsAuthed] = useState<boolean | null>(null);
  // Ensure auth cookie is set once on app load, then check login state
  useEffect(() => {
    (async () => {
      try {
        await api.get('/api/auth/ensure');
      } catch {}
      try {
        const me = await api.get('/api/auth/me');
        setIsAuthed(Boolean(me.data?.authenticated));
      } catch {
        setIsAuthed(false);
      } finally {
        setAuthChecked(true);
      }
    })();
  }, []);
  return (
    <div>
      <Suspense fallback={<div style={{ padding: 16 }}>Loading...</div>}>
        <Routes>
          <Route
            path="/"
            element={
              authChecked && isAuthed ? (
                <LandingPage />
              ) : authChecked ? (
                <LoginPage />
              ) : (
                <div style={{ padding: 16 }}>Loading...</div>
              )
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
        </Routes>
      </Suspense>
    </div>
  );
}

export default App;

// Uncomment this line to use CSS modules
// import styles from './app.module.css';

import { Route, Routes, Link } from 'react-router-dom';
import LandingPage from './Pages/LandingPage';

export function App() {
  return (
    <div>
      <Routes>
        <Route
          path="/"
          element={
            <LandingPage />
          }
        />
      </Routes>
    </div>
  );
}

export default App;

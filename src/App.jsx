import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast'; // Import Toaster
import Navbar from './components/Navbar';
import Home from './pages/Home';
import PostItem from './pages/PostItem';
import Dashboard from './pages/Dashboard'; 
import Auth from './components/Auth';

function App() {
  return (
    <BrowserRouter>
      {/* Global Toast Configuration */}
      <Toaster 
        position="top-center" 
        toastOptions={{ 
          style: { background: '#1e293b', color: '#f8fafc', border: '1px solid #334155' },
          success: { iconTheme: { primary: '#10b981', secondary: '#1e293b' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#1e293b' } }
        }} 
      />
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/post" element={<PostItem />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/auth" element={<Auth />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
export default App;
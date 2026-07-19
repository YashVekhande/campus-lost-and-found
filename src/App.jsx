import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import PostItem from './pages/PostItem';
import Dashboard from './pages/Dashboard'; 
import Auth from './components/Auth'; // <-- 1. Import the new Auth component

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/post" element={<PostItem />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/auth" element={<Auth />} /> {/* <-- 2. Add the Auth route */}
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
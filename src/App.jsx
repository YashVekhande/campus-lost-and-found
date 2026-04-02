import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import PostItem from './pages/PostItem';
import Dashboard from './pages/Dashboard'; // <-- Add this import

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/post" element={<PostItem />} />
          <Route path="/dashboard" element={<Dashboard />} /> {/* <-- Add this route */}
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
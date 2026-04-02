import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">Campus Lost & Found</Link>
      </div>
      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/post">Post Item</Link>
        <Link to="/dashboard">Dashboard</Link> {/* <-- Add this link */}
      </div>
    </nav>
  );
}
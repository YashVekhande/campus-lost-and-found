import { Link, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();
  
  // Read current user from localStorage
  const userString = localStorage.getItem('user');
  const user = userString ? JSON.parse(userString) : null;

  const handleSignOut = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/auth');
    window.location.reload();
  };

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">Campus Lost & Found</Link>
      </div>
      <div className="nav-links">
        <Link to="/">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
          Home
        </Link>
        <Link to="/post">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          Post Item
        </Link>
        <Link to="/dashboard">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>
          Dashboard
        </Link>

        {/* Dynamic Profile Section */}
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: '1rem' }}>
            <img 
              src={user.profilePic} 
              alt={user.username} 
              style={{ width: '32px', height: '32px', borderRadius: '50%', border: '2px solid var(--primary)' }} 
            />
            <span style={{ fontSize: '0.9rem', color: '#fff', fontWeight: '500' }}>{user.username}</span>
            <button onClick={handleSignOut} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
              Sign Out
            </button>
          </div>
        ) : (
          <Link to="/auth" style={{ color: 'var(--primary)', fontWeight: '600' }}>Sign In</Link>
        )}
      </div>
    </nav>
  );
}
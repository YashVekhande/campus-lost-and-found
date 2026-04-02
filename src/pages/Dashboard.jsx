import { useState } from 'react';
import axios from 'axios';

const API_URL = 'https://qwwbiwlmg8.execute-api.ap-south-1.amazonaws.com/prod';

export default function Dashboard() {
  const [email, setEmail] = useState('');
  const [items, setItems] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch the user's items and claims
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/dashboard`, { email });
      let data = response.data;
      if (typeof data === 'string') data = JSON.parse(data);
      
      setItems(data);
      setIsLoggedIn(true);
    } catch (error) {
      console.error("Dashboard fetch error:", error);
      alert("Failed to load dashboard.");
    } finally {
      setLoading(false);
    }
  };

  // Verify claim and delete the item
  const handleResolve = async (itemId) => {
    if (!window.confirm("Are you sure you want to verify this claim? This will remove the item from the public feed permanently.")) return;
    
    try {
      // Axios DELETE requires data to be passed in a specific 'data' object
      await axios.delete(`${API_URL}/dashboard`, { data: { itemId } });
      
      // Remove the item from the screen instantly
      setItems(items.filter(item => item.itemId !== itemId));
      alert("Item resolved successfully! It has been removed from the platform.");
      
    } catch (error) {
      console.error("Error resolving item:", error);
      alert("Failed to resolve item.");
    }
  };

  // 1. THE LOGIN SCREEN
  if (!isLoggedIn) {
    return (
      <div className="container" style={{ maxWidth: '500px', marginTop: '4rem' }}>
        <div className="item-card" style={{ textAlign: 'center' }}>
          <h2>My Dashboard</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            Enter the email you used to post items to view and verify claims.
          </p>
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input 
              type="email" required placeholder="student@university.edu"
              value={email} onChange={(e) => setEmail(e.target.value)}
              style={{ padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Accessing AWS...' : 'View My Items'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // 2. THE DASHBOARD SCREEN
  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Dashboard for {email}</h2>
        <button className="btn-secondary" onClick={() => setIsLoggedIn(false)}>Log Out</button>
      </div>

      {items.length === 0 ? (
        <p>You haven't posted any active items yet.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {items.map(item => (
            <div key={item.itemId} className="item-card" style={{ borderLeft: '4px solid var(--primary)' }}>
              
              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', borderBottom: '1px solid #e2e8f0', paddingBottom: '1rem', marginBottom: '1rem' }}>
                <img src={item.imageUrl} alt="Item" style={{ width: '80px', height: '80px', borderRadius: '8px' }} />
                <div>
                  <span className={`badge ${item.type}`}>{String(item.type).toUpperCase()}</span>
                  <p style={{ fontWeight: '600', marginTop: '0.5rem' }}>{item.description}</p>
                </div>
              </div>

              <h4 style={{ marginBottom: '0.5rem' }}>Claims on this item:</h4>
              {(!item.claims || item.claims.length === 0) ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No claims yet. Check back later.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {item.claims.map(claim => (
                    <div key={claim.claimId} style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <p><strong>{claim.claimerName}</strong> ({claim.claimerEmail}) says:</p>
                      <p style={{ fontStyle: 'italic', margin: '0.5rem 0', color: '#475569' }}>"{claim.message}"</p>
                      
                      <button 
                        style={{ backgroundColor: 'var(--success)', marginTop: '0.5rem' }}
                        onClick={() => handleResolve(item.itemId)}
                      >
                        Verify & Resolve Item
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
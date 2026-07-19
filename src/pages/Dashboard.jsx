import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;

export default function Dashboard() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('token');
  const userString = localStorage.getItem('user');
  const currentUser = userString ? JSON.parse(userString) : null;

  useEffect(() => {
    if (!token || !currentUser) {
      navigate('/auth');
      return;
    }

    const fetchDashboardItems = async () => {
      try {
        // FIX: Added the empty {} object before the headers configuration!
        const response = await axios.post(`${API_URL}/dashboard`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Ensure we always set an array, even if AWS returns null
        setItems(response.data || []);
      } catch (error) {
        console.error("Dashboard fetch error:", error);
        if (error.response?.status === 401) {
          alert("Session expired. Please log in again.");
          localStorage.clear();
          navigate('/auth');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardItems();
  }, [token, currentUser, navigate]);

  const handleResolve = async (itemId) => {
    if (!window.confirm("Are you sure you want to verify this claim? This will remove the item permanently.")) return;
    
    try {
      await axios.delete(`${API_URL}/dashboard`, { 
        headers: { Authorization: `Bearer ${token}` },
        data: { itemId } 
      });
      
      setItems(items.filter(item => item.itemId !== itemId));
    } catch (error) {
      console.error("Error resolving item:", error);
      alert("Failed to resolve item.");
    }
  };

  if (loading) return <h2 style={{ textAlign: 'center', marginTop: '3rem' }}>Loading Dashboard...</h2>;

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Dashboard for {currentUser?.username}</h2>
      </div>

      {items.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', background: 'var(--card-bg)', padding: '2rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
          You haven't posted any active items yet.
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {items.map(item => (
            <div key={item.itemId} className="item-card" style={{ borderLeft: '4px solid var(--primary)' }}>
              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1rem' }}>
                <img src={item.imageUrl} alt="Item" style={{ width: '80px', height: '80px', borderRadius: '8px', objectFit: 'cover' }} />
                <div>
                  <span className={`badge ${item.type}`}>{String(item.type).toUpperCase()}</span>
                  <p style={{ fontWeight: '600', marginTop: '0.5rem' }}>{item.description}</p>
                </div>
              </div>

              <h4 style={{ marginBottom: '0.5rem' }}>Claims on this item:</h4>
              {(!item.claims || item.claims.length === 0) ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No claims yet.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {item.claims.map(claim => (
                    <div key={claim.claimId} style={{ background: 'var(--bg-color)', padding: '1rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
                      <p><strong>{claim.claimerName}</strong> ({claim.claimerEmail}) says:</p>
                      <p style={{ fontStyle: 'italic', margin: '0.5rem 0', color: 'var(--text-muted)' }}>"{claim.message}"</p>
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
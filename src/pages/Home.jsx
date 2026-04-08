import { useState, useEffect } from 'react';
import axios from 'axios';
import ClaimModal from '../components/ClaimModal'; // <-- Import our new Modal

const API_URL = import.meta.env.VITE_API_URL;

export default function Home() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // New state to control the modal
  const [selectedItemToClaim, setSelectedItemToClaim] = useState(null); 

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await axios.get(`${API_URL}/items`);
        let data = response.data;
        if (typeof data === 'string') data = JSON.parse(data);

        if (Array.isArray(data)) {
          data.sort((a, b) => new Date(b.postedAt || 0) - new Date(a.postedAt || 0));
          setItems(data);
        }
        setLoading(false);
      } catch (err) {
        console.error("Error fetching items:", err);
        setError("Failed to load items from AWS.");
        setLoading(false);
      }
    };
    fetchItems();
  }, []);

  if (loading) return <h2 style={{ textAlign: 'center', marginTop: '3rem' }}>Fetching from AWS now....</h2>;
  if (error) return <h2 style={{ textAlign: 'center', color: 'var(--danger)', marginTop: '3rem' }}>{error}</h2>;

  return (
    <div className="container">
      <h1 style={{ marginBottom: '1rem' }}>Recent Activity</h1>
      
      <div className="items-grid">
        {items.length === 0 ? <p>No items found. Be the first to post!</p> : (
          items.map((item) => (
            <div key={item.itemId} className="item-card">
              
              <img 
                src={item.imageUrl || 'https://placehold.co/400x250?text=No+Image'} 
                alt="item" 
                onError={(e) => { e.target.src = 'https://placehold.co/400x250?text=Image+Error'; }}
              />
              
              <span className={`badge ${String(item.type || 'lost').toLowerCase()}`}>
                {String(item.type || 'LOST').toUpperCase()}
              </span>

              <p style={{ flexGrow: 1, fontWeight: '500' }}>
                {item.description || "No description provided."}
              </p>
              
              <div className="tag-container">
                {!item.tags || item.tags.length === 0 ? (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>AI analyzing...</span>
                ) : (
                  item.tags.map((tag, index) => (
                    <span key={index} className="tag-pill">{tag}</span>
                  ))
                )}
              </div>
              
              {/* Clicking this sets the item into state, which opens the modal */}
              <button 
                onClick={() => setSelectedItemToClaim(item)}
                style={{ marginTop: 'auto', width: '100%' }}
              >
                Claim Item
              </button>
            </div>
          ))
        )}
      </div>

      {/* The Dynamic Modal Component */}
      <ClaimModal 
        item={selectedItemToClaim} 
        onClose={() => setSelectedItemToClaim(null)} 
      />
    </div>
  );
}
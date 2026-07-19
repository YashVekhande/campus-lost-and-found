import { useState, useEffect } from 'react';
import axios from 'axios';
import ClaimModal from '../components/ClaimModal'; 

const API_URL = import.meta.env.VITE_API_URL;

export default function Home() {
  const [items, setItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState(''); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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

  // Filter items based on the search query (checks description)
  const filteredItems = items.filter(item => {
    const query = searchQuery.toLowerCase();
    const matchesDescription = item.description?.toLowerCase().includes(query);
    // We can still secretly check backend tags if they exist, without showing them
    const matchesTags = item.tags?.some(tag => tag.toLowerCase().includes(query));
    
    return matchesDescription || matchesTags;
  });

  if (loading) return <h2 style={{ textAlign: 'center', marginTop: '3rem' }}>Fetching from AWS...</h2>;
  if (error) return <h2 style={{ textAlign: 'center', color: 'var(--danger)', marginTop: '3rem' }}>{error}</h2>;

  return (
    <div className="container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: '800', letterSpacing: '-1px' }}>Recent Activity</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>Help your campus community recover their items.</p>
      </div>
      
      {/* Search Bar UI */}
      <div style={{ marginBottom: '2rem' }}>
        <input 
          type="text" 
          placeholder="Search by item description..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '14px 20px',
            borderRadius: '12px',
            border: '1px solid var(--border)',
            background: 'var(--card-bg)',
            color: 'var(--text-main)',
            fontSize: '1rem',
            boxShadow: 'var(--shadow)'
          }}
        />
      </div>
      
      <div className="items-grid">
        {filteredItems.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>
            {searchQuery ? "No items match your search." : "No items found. Be the first to post!"}
          </p>
        ) : (
          filteredItems.map((item) => (
            <div key={item.itemId} className="item-card">
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingBottom: '4px' }}>
                <img 
                  src={item.profilePic || `https://ui-avatars.com/api/?name=Student&background=random`} 
                  alt="Poster Profile" 
                  style={{ width: '28px', height: '28px', borderRadius: '50%' }}
                />
                <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#e2e8f0' }}>
                  {item.username || 'Anonymous Student'}
                </span>
              </div>

              <img 
                src={item.imageUrl || 'https://placehold.co/400x250/1e293b/94a3b8?text=No+Image'} 
                alt="item" 
                onError={(e) => { e.target.src = 'https://placehold.co/400x250/1e293b/ef4444?text=Image+Error'; }}
              />
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className={`badge ${String(item.type || 'lost').toLowerCase()}`}>
                  {String(item.type || 'LOST').toUpperCase()}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {item.postedAt ? new Date(item.postedAt).toLocaleDateString() : 'Recently'}
                </span>
              </div>

              {/* The description now takes center stage */}
              <p style={{ flexGrow: 1, fontWeight: '500', fontSize: '1.05rem', marginBottom: '1rem' }}>
                {item.description || "No description provided."}
              </p>
              
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

      {selectedItemToClaim && (
        <ClaimModal 
          item={selectedItemToClaim} 
          onClose={() => setSelectedItemToClaim(null)} 
        />
      )}
    </div>
  );
}
import { useState } from 'react';
import axios from 'axios';

// Using your secure environment variable
const API_URL = import.meta.env.VITE_API_URL;

export default function ClaimModal({ item, onClose }) {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [status, setStatus] = useState('idle'); // idle, loading, success, error

  if (!item) return null; // Don't render if no item is selected

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('loading');

    try {
      await axios.post(`${API_URL}/claims`, {
        itemId: item.itemId,
        claimerName: formData.name,
        claimerEmail: formData.email,
        message: formData.message
      });
      setStatus('success');
    } catch (error) {
      console.error("Claim error:", error);
      setStatus('error');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        
        {status === 'success' ? (
          <div style={{ textAlign: 'center', padding: '2rem 0' }}>
            <h2 style={{ color: 'var(--success)', marginBottom: '1rem' }}>Claim Submitted!</h2>
            <p>Your message has been securely sent to our AWS Database. The person who posted this will be notified.</p>
            <button onClick={onClose} style={{ marginTop: '1.5rem', width: '100%' }}>Close</button>
          </div>
        ) : (
          <>
            <h2>Claim this {item.tags && item.tags[0] ? item.tags[0] : 'Item'}</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
              Provide your details to prove ownership or arrange a meetup.
            </p>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
              <input 
                type="text" required placeholder="Your Full Name" 
                value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
              <input 
                type="email" required placeholder="Your Student Email" 
                value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
              <textarea 
                required rows="3" placeholder="Identify a unique scratch, what's inside, or where you lost it..."
                value={formData.message} onChange={(e) => setFormData({...formData, message: e.target.value})}
              />
              
              {status === 'error' && <p style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>Network error. Try again.</p>}
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" className="btn-secondary" onClick={onClose} disabled={status === 'loading'}>
                  Cancel
                </button>
                <button type="submit" disabled={status === 'loading'}>
                  {status === 'loading' ? 'Sending to AWS...' : 'Submit Claim'}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
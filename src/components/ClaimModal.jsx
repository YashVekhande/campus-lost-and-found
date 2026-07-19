import { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export default function ClaimModal({ item, onClose }) {
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const userString = localStorage.getItem('user');
  const currentUser = userString ? JSON.parse(userString) : null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!currentUser) {
      alert("You must be logged in to claim an item.");
      return;
    }
    
    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/claims`, {
        itemId: item.itemId,
        claimerName: currentUser.username,
        claimerEmail: currentUser.email,
        message: message
      });
      alert("Claim submitted successfully! The owner has been notified.");
      onClose();
    } catch (error) {
      console.error(error);
      alert("Failed to submit claim. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  // Truncate the description so the title doesn't overflow
  const shortDescription = item.description && item.description.length > 40 
    ? item.description.substring(0, 40) + "..." 
    : item.description;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        
        {/* Title now dynamically uses the actual description */}
        <h2 style={{ marginBottom: '1rem', fontSize: '1.4rem' }}>
          Claim: {shortDescription || 'Item'}
        </h2>
        
        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.9rem' }}>
          Send a message to <strong>{item.username || 'the owner'}</strong> to prove this is yours.
        </p>
        
        <form onSubmit={handleSubmit}>
          <textarea 
            required
            rows="4"
            placeholder="Describe specific details about the item (e.g. scratches, contents, lock screen wallpaper)..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            style={{ 
              width: '100%', padding: '12px', 
              background: 'var(--bg-color)', color: 'var(--text-main)',
              border: '1px solid var(--border)', borderRadius: '8px'
            }}
          ></textarea>
          
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={submitting}>
              {submitting ? 'Sending...' : 'Send Claim'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
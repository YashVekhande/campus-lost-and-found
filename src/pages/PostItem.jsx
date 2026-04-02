import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = 'https://qwwbiwlmg8.execute-api.ap-south-1.amazonaws.com/prod';
const BUCKET_NAME = 'campus-lostfound-yash'; 
const REGION = 'ap-south-1';

export default function PostItem() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    type: 'lost',
    description: '',
    contactEmail: '',
    file: null
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.file) return alert("Please select an image!");
    
    setUploading(true);

    try {
      const itemId = crypto.randomUUID();
      const fileExt = formData.file.name.split('.').pop();
      const fileName = `${itemId}.${fileExt}`;
      const s3Url = `https://${BUCKET_NAME}.s3.${REGION}.amazonaws.com/${fileName}`;

      await axios.put(s3Url, formData.file, {
        headers: { 'Content-Type': formData.file.type }
      });

      const itemData = {
        itemId: itemId,
        type: formData.type,
        description: formData.description,
        imageUrl: s3Url,
        contactEmail: formData.contactEmail
      };

      await axios.post(`${API_URL}/items`, itemData);

      alert("Success! The AI is currently analyzing your photo.");
      navigate('/'); 
      
    } catch (error) {
      console.error("Error posting item:", error);
      alert("Something went wrong. Check the console.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '600px' }}>
      <div className="item-card">
        <h2 style={{ marginBottom: '1.5rem' }}>Post an Item</h2>
        
        {/* Notice how clean the form is now without inline styles! */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          
          <div>
            <label style={{ fontWeight: '500', display: 'block', marginBottom: '0.5rem' }}>Item Type:</label>
            <select 
              value={formData.type} 
              onChange={(e) => setFormData({...formData, type: e.target.value})}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
            >
              <option value="lost">Lost</option>
              <option value="found">Found</option>
            </select>
          </div>

          <div>
            <label style={{ fontWeight: '500', display: 'block', marginBottom: '0.5rem' }}>Description:</label>
            <textarea 
              required rows="3"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontFamily: 'inherit' }}
              placeholder="e.g., Left my blue hydroflask in the library..."
            />
          </div>

          <div>
            <label style={{ fontWeight: '500', display: 'block', marginBottom: '0.5rem' }}>Contact Email:</label>
            <input 
              type="email" required
              value={formData.contactEmail}
              onChange={(e) => setFormData({...formData, contactEmail: e.target.value})}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
            />
          </div>

          <div>
            <label style={{ fontWeight: '500', display: 'block', marginBottom: '0.5rem' }}>Upload Photo:</label>
            <input 
              type="file" accept="image/*" required
              onChange={(e) => setFormData({...formData, file: e.target.files[0]})}
              style={{ width: '100%', padding: '10px', border: '1px dashed #cbd5e1', borderRadius: '6px', background: '#f8fafc' }}
            />
            <small style={{ color: 'var(--text-muted)', display: 'block', marginTop: '4px' }}>
              Required for AI Tagging
            </small>
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button 
              type="button" 
              className="btn-secondary" 
              style={{ flex: 1 }}
              onClick={() => navigate('/')}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={uploading}
              style={{ flex: 2 }}
            >
              {uploading ? 'Uploading to AWS...' : 'Submit Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
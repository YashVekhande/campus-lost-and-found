import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;
const BUCKET_NAME = import.meta.env.VITE_BUCKET_NAME; 
const REGION = import.meta.env.VITE_REGION;

export default function PostItem() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  
  const userString = localStorage.getItem('user');
  const currentUser = userString ? JSON.parse(userString) : null;

  // Security Guard: Boot unauthorized users to /auth
  useEffect(() => {
    if (!currentUser) {
      alert("You must be logged in to post items!");
      navigate('/auth');
    }
  }, [currentUser, navigate]);

  const [formData, setFormData] = useState({
    type: 'lost',
    description: '',
    file: null
  });

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({ ...formData, file });
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.file) return alert("Please select an image!");
    if (!currentUser) return;
    
    setUploading(true);

    try {
      const itemId = crypto.randomUUID();
      const fileExt = formData.file.name.split('.').pop();
      const fileName = `${itemId}.${fileExt}`;
      const s3Url = `https://${BUCKET_NAME}.s3.${REGION}.amazonaws.com/${fileName}`;

      await axios.put(s3Url, formData.file, {
        headers: { 'Content-Type': formData.file.type }
      });

      // Construct item payload containing the poster's profile data
      const itemData = {
        itemId: itemId,
        type: formData.type,
        description: formData.description,
        imageUrl: s3Url,
        contactEmail: currentUser.email,        // Pulled securely from user session
        username: currentUser.username,          // Saved explicitly for fast UI display
        profilePic: currentUser.profilePic        // Saved explicitly for fast UI display
      };

      await axios.post(`${API_URL}/items`, itemData);

      alert("Success! The AI is currently analyzing your photo.");
      navigate('/'); 
      
    } catch (error) {
      console.error("Error posting item:", error);
      alert("Something went wrong.");
    } finally {
      setUploading(false);
    }
  };

  if (!currentUser) return null;

  return (
    <div className="post-page-wrapper">
      <div className="post-glass-card">
        <h2>Post an Item</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="modern-form-group">
            <label>Item Type:</label>
            <select 
              className="modern-select"
              value={formData.type} 
              onChange={(e) => setFormData({...formData, type: e.target.value})}
            >
              <option value="lost">Lost</option>
              <option value="found">Found</option>
            </select>
          </div>

          <div className="modern-form-group">
            <label>Description:</label>
            <textarea 
              className="modern-textarea"
              required 
              rows="3"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="e.g., Left my blue hydroflask in the library..."
            ></textarea>
          </div>

          <div className="modern-form-group">
            <label>Upload Photo:</label>
            <label className="file-upload-label">
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="preview-image" />
              ) : (
                <span>Click to browse for a photo</span>
              )}
              <input type="file" accept="image/*" required onChange={handleFileChange} />
            </label>
            <small style={{ color: '#94a3b8', fontSize: '0.8rem', marginTop: '4px' }}>
              Required for AI Tagging
            </small>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-modern btn-cancel" onClick={() => navigate('/')}>
              Cancel
            </button>
            <button type="submit" className="btn-modern btn-submit" disabled={uploading}>
              {uploading ? 'Uploading...' : 'Submit Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
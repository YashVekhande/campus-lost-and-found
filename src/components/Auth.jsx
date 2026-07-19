import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState(''); // <-- NEW: State for username
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    const endpoint = isLogin ? '/login' : '/register';
    // Send username only during registration
    const payload = isLogin ? { email, password } : { email, password, username };
    
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Authentication failed');
      }

      if (isLogin) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user)); // <-- NEW: Save user object
        setMessage('Login successful! Welcome back.');
        
        setTimeout(() => {
          navigate('/');
          window.location.reload(); // Quick refresh to update user state in Navbar
        }, 1000);
      } else {
        setMessage('Account created! Please log in.');
        setIsLogin(true);
        setPassword('');
      }
    } catch (err) {
      setMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const isSuccessMessage = message.includes('success') || message.includes('created');

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>{isLogin ? 'Sign In to Campus L&F' : 'Create an Account'}</h2>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <div>
              <label>Username</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="auth-input"
                placeholder="Choose a unique username"
              />
            </div>
          )}

          <div>
            <label>Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="auth-input"
              placeholder="student@campus.edu"
            />
          </div>
          
          <div>
            <label>Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input"
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={isLoading} className="auth-button">
            {isLoading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        {message && (
          <div className={`auth-message ${isSuccessMessage ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <div className="auth-toggle">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setMessage('');
            }}
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
}
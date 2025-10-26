import React, { useState } from 'react';
import axios from 'axios';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLogin, setIsLogin] = useState(true);
    const [message, setMessage] = useState('');
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [userData, setUserData] = useState(null);

    // В production используем относительные пути, nginx проксирует к бэкенду
    const API_BASE = process.env.NODE_ENV === 'development' ? '' : '/api';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');

        try {
            if (isLogin) {
                // Логин
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);
                
                const response = await axios.post(`${API_BASE}/login`, formData, {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                });
                
                const { access_token } = response.data;
                setToken(access_token);
                localStorage.setItem('token', access_token);
                setMessage('Login successful!');
                
                // Получаем данные пользователя
                await fetchUserData(access_token);
            } else {
                // Регистрация
                await axios.post(`${API_BASE}/register`, {
                    email,
                    password
                });
                
                setMessage('Registration successful! Please login.');
                setIsLogin(true);
                setEmail('');
                setPassword('');
            }
        } catch (error) {
            setMessage(error.response?.data?.detail || 'An error occurred');
        }
    };

    const fetchUserData = async (userToken) => {
        try {
            const response = await axios.get(`${API_BASE}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${userToken}`
                }
            });
            setUserData(response.data);
        } catch (error) {
            console.error('Failed to fetch user data:', error);
        }
    };

    const handleLogout = () => {
        setToken(null);
        setUserData(null);
        localStorage.removeItem('token');
        setMessage('Logged out successfully');
    };

    if (token && userData) {
        return (
            <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
                <h2>Welcome!</h2>
                <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '5px' }}>
                    <p><strong>Email:</strong> {userData.email}</p>
                    <p><strong>User ID:</strong> {userData.id}</p>
                    <p><strong>Joined:</strong> {new Date(userData.created_at).toLocaleDateString()}</p>
                </div>
                <button 
                    onClick={handleLogout}
                    style={{
                        marginTop: '15px',
                        padding: '10px 20px',
                        backgroundColor: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Logout
                </button>
            </div>
        );
    }

    return (
        <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
            <h2>{isLogin ? 'Login' : 'Register'}</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '15px' }}>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{
                            width: '100%',
                            padding: '8px',
                            marginTop: '5px',
                            border: '1px solid #ddd',
                            borderRadius: '4px'
                        }}
                    />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{
                            width: '100%',
                            padding: '8px',
                            marginTop: '5px',
                            border: '1px solid #ddd',
                            borderRadius: '4px'
                        }}
                    />
                </div>
                <button
                    type="submit"
                    style={{
                        width: '100%',
                        padding: '10px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    {isLogin ? 'Login' : 'Register'}
                </button>
            </form>
            
            {message && (
                <div style={{
                    marginTop: '15px',
                    padding: '10px',
                    backgroundColor: message.includes('success') ? '#d4edda' : '#f8d7da',
                    border: `1px solid ${message.includes('success') ? '#c3e6cb' : '#f5c6cb'}`,
                    borderRadius: '4px',
                    color: message.includes('success') ? '#155724' : '#721c24'
                }}>
                    {message}
                </div>
            )}
            
            <p style={{ marginTop: '15px', textAlign: 'center' }}>
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                    onClick={() => {
                        setIsLogin(!isLogin);
                        setMessage('');
                    }}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#007bff',
                        cursor: 'pointer',
                        textDecoration: 'underline'
                    }}
                >
                    {isLogin ? 'Register' : 'Login'}
                </button>
            </p>
        </div>
    );
};

export default Login;
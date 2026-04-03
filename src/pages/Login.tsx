import { Link, useNavigate } from 'react-router-dom'
import { useState, FormEvent } from 'react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data?.message || 'Invalid credentials')
      }

      localStorage.setItem('userId', data.userId)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', paddingTop: '72px' }}>
      <div style={{
        background: 'rgba(10, 10, 12, 0.6)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '20px',
        padding: '40px',
        width: '100%',
        maxWidth: '420px',
        textAlign: 'center',
        boxShadow: '0 30px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)'
      }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '8px' }}>Welcome Back</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Log in to your EDI intelligence portal.</p>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <input 
            type="email" 
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none' }} 
          />
          <input 
            type="password" 
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none' }} 
          />
          
          {error && (
            <p style={{ color: '#ff4d4f', margin: '0', fontSize: '0.875rem', textAlign: 'left' }}>
              {error}
            </p>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading}
            style={{ 
              width: '100%', 
              padding: '14px', 
              marginTop: '16px',
              opacity: loading ? 0.7 : 1,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={{ marginTop: '24px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Don't have an account? <Link to="/signup" style={{ color: '#fff', textDecoration: 'none' }}>Sign up</Link>
        </p>
      </div>
    </div>
  )
}

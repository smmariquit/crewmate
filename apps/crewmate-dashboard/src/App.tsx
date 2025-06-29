import { useState } from 'react'
import './App.css'

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <div className="app">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-icon">🚀</span>
            <span className="logo-text">Crewmate</span>
          </div>
          
          <div className={`nav-menu ${isMenuOpen ? 'active' : ''}`}>
            <a href="#features" className="nav-link">Features</a>
            <a href="#about" className="nav-link">About</a>
            <a href="#contact" className="nav-link">Contact</a>
            <button className="cta-button">Get Started</button>
          </div>
          
          <div 
            className={`hamburger ${isMenuOpen ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Manage Your Crew with
              <span className="highlight"> Intelligence</span>
            </h1>
            <p className="hero-subtitle">
              Streamline team coordination, track assets, and boost productivity 
              with our AI-powered crew management platform.
            </p>
            <div className="hero-buttons">
              <button className="primary-button">Start Free Trial</button>
              <button className="secondary-button">Watch Demo</button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="dashboard-preview">
              <div className="preview-header">
                <div className="preview-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
              <div className="preview-content">
                <div className="preview-card"></div>
                <div className="preview-card"></div>
                <div className="preview-card"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <h2 className="section-title">Why Choose Crewmate?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI-Powered Insights</h3>
              <p>Get intelligent recommendations and automated task management powered by advanced AI.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Real-time Analytics</h3>
              <p>Monitor team performance and asset growth with comprehensive real-time dashboards.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔗</div>
              <h3>Seamless Integration</h3>
              <p>Connect with Discord and other platforms for unified team communication.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Lightning Fast</h3>
              <p>Built with modern technology for instant responses and smooth user experience.</p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about">
        <div className="container">
          <div className="about-content">
            <div className="about-text">
              <h2>Built for Modern Teams</h2>
              <p>
                Crewmate is designed to help teams work smarter, not harder. 
                Our platform combines the power of AI with intuitive design to 
                create a seamless crew management experience.
              </p>
              <ul className="about-features">
                <li>✓ Discord Bot Integration</li>
                <li>✓ Asset Growth Tracking</li>
                <li>✓ Real-time Collaboration</li>
                <li>✓ Advanced Analytics</li>
              </ul>
            </div>
            <div className="about-visual">
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-number">99%</div>
                  <div className="stat-label">Uptime</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">2s</div>
                  <div className="stat-label">Response Time</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">24/7</div>
                  <div className="stat-label">Support</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="contact">
        <div className="container">
          <h2>Ready to Get Started?</h2>
          <p>Join thousands of teams already using Crewmate to boost their productivity.</p>
          <button className="primary-button large">Start Your Free Trial</button>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <span className="logo-icon">🚀</span>
              <span className="logo-text">Crewmate</span>
            </div>
            <div className="footer-links">
              <a href="#features">Features</a>
              <a href="#about">About</a>
              <a href="#contact">Contact</a>
              <a href="/privacy">Privacy</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 Crewmate. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

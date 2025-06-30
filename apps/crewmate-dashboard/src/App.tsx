import { useState, useEffect, useRef } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import './App.css'

const platformWidgets = [
  {
    name: 'Discord',
    server: '1388787204326817863',
    channel: '1388787205052305489',
    icon: 'https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/discord.svg',
    demoUrl: 'https://discord.gg/your-demo-link',
  },
  {
    name: 'Slack',
    server: 'slack-server-id',
    channel: 'slack-channel-id',
    icon: 'https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/slack.svg',
    demoUrl: 'https://slack.com/your-demo-link',
  },
  {
    name: 'Telegram',
    server: 'telegram-server-id',
    channel: 'telegram-channel-id',
    icon: 'https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/telegram.svg',
    demoUrl: 'https://t.me/your-demo-link',
  },
  {
    name: 'MS Teams',
    server: 'teams-server-id',
    channel: 'teams-channel-id',
    icon: 'https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/microsoftteams.svg',
    demoUrl: 'https://teams.microsoft.com/your-demo-link',
  },
]

function WidgetBotCarousel() {
  const [index, setIndex] = useState(0)
  const current = platformWidgets[index]
  return (
    <div className="widgetbot-carousel">
      <div className="carousel-header">
        {platformWidgets.map((w, i) => (
          <button
            key={w.name}
            className={`carousel-dot${i === index ? ' active' : ''}`}
            onClick={() => setIndex(i)}
            aria-label={`Show ${w.name} demo`}
          >
            <img src={w.icon} alt={w.name} style={{ width: 24, height: 24 }} />
          </button>
        ))}
      </div>
      {current.name === 'Discord' ? (
        <WidgetBotEmbed server={current.server} channel={current.channel} />
      ) : (
        <div className="coming-soon-demo">
          <span className="coming-soon-text">{current.name} Demo Coming Soon!</span>
        </div>
      )}
      <div className="carousel-footer">
        <span>{current.name} Demo</span>
        {current.name === 'Discord' && (
          <a href={current.demoUrl} target="_blank" rel="noopener noreferrer" className="join-demo-btn">
            Join Demo {current.name}
          </a>
        )}
      </div>
    </div>
  )
}

function WidgetBotEmbed({ server = '1388787204326817863', channel = '1388787205052305489' }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!ref.current) return
    ref.current.innerHTML = ''
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/@widgetbot/html-embed'
    script.async = true
    ref.current.appendChild(script)
    const widget = document.createElement('widgetbot')
    widget.setAttribute('server', server)
    widget.setAttribute('channel', channel)
    widget.setAttribute('width', '100%')
    widget.setAttribute('height', '540')
    ref.current.appendChild(widget)
    return () => {
      if (ref.current) ref.current.innerHTML = ''
    }
  }, [server, channel])
  return <div className="widgetbot-container large" ref={ref}></div>
}

function PlatformRow() {
  return (
    <div className="platform-row">
      <span className="platform-badge">Multi-Platform Bot</span>
      <div className="platform-icons">
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/discord.svg" alt="Discord" title="Discord" />
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/telegram.svg" alt="Telegram" title="Telegram" />
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/whatsapp.svg" alt="WhatsApp" title="WhatsApp" />
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/slack.svg" alt="Slack" title="Slack" />
        <span className="platform-more">+ more</span>
      </div>
      <div className="platform-caption">Integrates with Discord, Telegram, WhatsApp, Slack, and more!</div>
    </div>
  )
}

function ScrollIndicator() {
  return (
    <div className="scroll-indicator">
      <span className="arrow"></span>
    </div>
  )
}

function Navbar() {
  const navigate = useNavigate()
  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-logo" onClick={() => navigate('/')}>🚀 Crewmate</div>
        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#testimonials">Testimonials</a>
          <a href="#pricing">Pricing</a>
          <button className="cta-button" onClick={() => navigate('/dashboard')}>Sign In</button>
        </div>
      </div>
    </nav>
  )
}

function AmongUsAttribution() {
  return (
    <div className="amongus-attribution">
      <span style={{ fontSize: '0.95em', color: '#888' }}>
        <strong>Disclaimer:</strong> Crewmate is a fan-made project and is not affiliated with Among Us or Innersloth LLC. All trademarks are property of their respective owners.
      </span>
    </div>
  )
}

function FeaturesSection() {
  return (
    <section className="features" id="features">
      <h2 className="section-title">Features</h2>
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🛠️</div>
          <h3>Direct Platform Integration</h3>
          <p>No new platform to learn—Crewmate works natively inside Discord, Slack, Telegram, and Teams.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🧠</div>
          <h3>AI-Powered Commands</h3>
          <p>Use natural language to assign tasks, check progress, and automate workflows.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">📈</div>
          <h3>Real-Time Analytics</h3>
          <p>Instantly see team activity, engagement, and growth across all platforms.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🔒</div>
          <h3>Privacy-First</h3>
          <p>Your data stays secure and private—no unnecessary data collection.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">⚡</div>
          <h3>Lightning Fast Onboarding</h3>
          <p>Get started in seconds—no complex setup or migration required.</p>
        </div>
      </div>
    </section>
  )
}

function TestimonialsSection() {
  return (
    <section className="testimonials" id="testimonials">
      <h2 className="section-title">Testimonials</h2>
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">"</div>
          <h3>"Crewmate made project management fun and seamless for our Discord community!"</h3>
          <p>- Alex, Community Manager</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">"</div>
          <h3>"We love that we didn't have to move to a new tool—Crewmate just works in Slack!"</h3>
          <p>- Priya, Startup Founder</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">"</div>
          <h3>"The analytics and AI commands are next-level. Our team is more productive than ever."</h3>
          <p>- Jordan, Team Lead</p>
        </div>
      </div>
    </section>
  )
}

function PricingSection() {
  return (
    <section className="pricing" id="pricing">
      <h2 className="section-title">Pricing</h2>
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🆓</div>
          <h3>Free</h3>
          <p>Basic features for small teams and communities. $0/month.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">💼</div>
          <h3>Pro</h3>
          <p>Advanced analytics, unlimited integrations, and priority support. $9/month.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🏢</div>
          <h3>Enterprise</h3>
          <p>Custom solutions, dedicated onboarding, and enhanced security. Contact us for pricing.</p>
        </div>
      </div>
    </section>
  )
}

function HeroPage() {
  const navigate = useNavigate()
  return (
    <div className="hero-saas hero-animated-bg amongus-bg">
      <Navbar />
      <section className="hero-content-saas amongus-hero">
        <div className="hero-left fade-in-up amongus-left">
          <PlatformRow />
          <h1 className="hero-title amongus-title">
            <span className="highlight">Crewmate</span> —<br />
            Project Management <span style={{ color: '#ff6b6b' }}>Inside</span> Your Favorite Platforms
          </h1>
          <p className="hero-subtitle amongus-subtitle">
            No new tools. Crewmate works directly in Discord, Slack, Telegram, and Teams.<br />
            <span style={{ color: '#ff6b6b', fontWeight: 600 }}>No migration. Just productivity.</span>
          </p>
          <ul className="hero-features amongus-features">
            <li>🛠️ Native integration</li>
            <li>🧠 AI commands</li>
            <li>📈 Analytics</li>
            <li>🔒 Privacy-first</li>
            <li>⚡ Fast onboarding</li>
          </ul>
          <div className="hero-cta-row amongus-cta">
            <button className="primary-button" onClick={() => navigate('/login')}>Get Started Free</button>
            <a href="#features" className="secondary-link">Learn More</a>
            <a href="https://discord.gg/your-demo-link" target="_blank" rel="noopener noreferrer" className="join-demo-btn amongus-btn">Join Demo Discord</a>
          </div>
          <AmongUsAttribution />
        </div>
        <div className="hero-right slide-in-right amongus-right">
          <WidgetBotCarousel />
        </div>
      </section>
      <ScrollIndicator />
    </div>
  )
}

function DashboardPage() {
  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        <div className="sidebar-logo-row">
          <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/discord.svg" alt="Crewmate Logo" className="sidebar-logo" />
          <span className="sidebar-title">DASHBOARD</span>
        </div>
        <nav className="sidebar-nav">
          <button className="sidebar-link active">Dashboard</button>
          <button className="sidebar-link">Tasks</button>
          <button className="sidebar-link">Performance</button>
          <button className="sidebar-link">Team</button>
        </nav>
      </aside>
      <main className="dashboard-main-area">
        <header className="dashboard-header">
          <button className="sidebar-menu-btn">☰</button>
          <input className="dashboard-search" placeholder="SEARCH BUTTON" />
          <button className="dashboard-profile-btn">User</button>
        </header>
        <section className="dashboard-progress-section">
          <div className="progress-bar-label">Progress Bar</div>
          <div className="progress-bar"></div>
          <div className="dashboard-tabs">
            <button className="tab active">Upcoming Tasks</button>
            <button className="tab">All Tasks</button>
          </div>
          <div className="dashboard-tasks-columns">
            <div className="task-column">
              <div className="column-title">On Progress</div>
              <div className="task-card">Task #1</div>
              <div className="task-card">Task #2</div>
              <button className="add-task-btn">ADD TASK</button>
            </div>
            <div className="task-column">
              <div className="column-title">Pending Tasks</div>
              <div className="task-card">Task #1</div>
              <div className="task-card">Task #2</div>
              <button className="add-task-btn">ADD TASK</button>
            </div>
            <div className="task-column">
              <div className="column-title">Completed Tasks</div>
              <div className="task-card">Task #1</div>
              <div className="task-card">Task #2</div>
              <button className="add-task-btn">ADD TASK</button>
            </div>
          </div>
        </section>
      </main>
      <aside className="dashboard-rightbar">
        <div className="rightbar-header">
          <button className="rightbar-tab active">CALENDAR</button>
          <button className="rightbar-tab">NOTIFICATIONS</button>
        </div>
        <div className="rightbar-calendar">CALENDAR OF TASKS</div>
        <div className="rightbar-tasks">TASKS</div>
      </aside>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={
        <>
          <HeroPage />
          <FeaturesSection />
          <TestimonialsSection />
          <PricingSection />
        </>
      } />
      <Route path="/dashboard" element={<DashboardPage />} />
    </Routes>
  )
}

export default App

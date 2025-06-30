import { useState, useEffect, useRef } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import './App.css'
import logo from '../assets/logo.png'
import amogus32Dance from '../assets/32 bit Amogus/Dance.gif'
import amogus16 from '../assets/16 bit Amogus/16 bit Amogus.png'
import amogus8Flip from '../assets/8 bit Amogus/Flip.gif'

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

function WidgetBotEmbed({ server = '1388787204326817863', channel = '1389091611681488976' }) {
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
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/discord.svg" alt="Discord" title="Discord" className="platform-icon colored" />
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/telegram.svg" alt="Telegram" title="Telegram" className="platform-icon colored" />
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/whatsapp.svg" alt="WhatsApp" title="WhatsApp" className="platform-icon colored" />
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/slack.svg" alt="Slack" title="Slack" className="platform-icon colored" />
        <span className="platform-more" style={{ color: '#fff' }}>+ more</span>
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
        <img src={logo} alt="Crewmate Logo" className="main-logo" onClick={() => navigate('/')} />
        <div className="nav-logo" onClick={() => navigate('/')}>Crewmate</div>
        <div className="nav-links">
          <a href="#features">Features</a>
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
      <span style={{ fontSize: '0.95em' }}>
        <strong>Disclaimer:</strong> Crewmate is a fan-made project and is not affiliated with Among Us or Innersloth LLC. All trademarks are property of their respective owners.
      </span>
    </div>
  )
}

function FeaturesSection() {
  return (
    <section className="features" id="features">
      <h2 className="section-title">Features</h2>
      <img src={amogus16} alt="16 bit Crewmate" className="amongus-character amongus-green" />
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🛠️</div>
          <h3>Direct Platform Integration</h3>
          <p>No new platform to learn—Crewmate works natively inside Discord, Slack, Telegram, and Teams.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🧠</div>
          <h3>Natural Language Processing</h3>
          <p>Smartly understands your intent and actions with minimal setup—just type what you want to do.</p>
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

function PricingSection() {
  return (
    <section className="pricing" id="pricing">
      <h2 className="section-title">Pricing</h2>
      <img src={amogus8Flip} alt="8 bit Crewmate Flip" className="amongus-character amongus-yellow" />
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🆓</div>
          <h3>Free Tier</h3>
          <p>Get started for free with basic features and single-platform access.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">💸</div>
          <h3>All Platform Access</h3>
          <p>Unlock all platforms and advanced features for just $5/month.</p>
        </div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <span className="footer-brand">Crewmate</span>
        <span>© {new Date().getFullYear()} Crewmate. Not affiliated with Among Us or Innersloth LLC.</span>
      </div>
    </footer>
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
          <img src={amogus32Dance} alt="Dancing Crewmate" className="amongus-character amongus-red" />
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
            <li>🧠 Natural Language Processing</li>
            <li>📈 Analytics</li>
            <li>🔒 Privacy-first</li>
            <li>⚡ Fast onboarding</li>
          </ul>
          <div className="hero-cta-row amongus-cta">
            <button className="primary-button" onClick={() => navigate('/dashboard')}>Get Started Free</button>
            <a href="https://discord.gg/Q2fQyfXk" target="_blank" rel="noopener noreferrer" className="join-demo-btn amongus-btn">Join Demo Discord</a>
          </div>
          <div className="demo-note"><strong>No need to join the server to try the demo!</strong></div>
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
  const [tab, setTab] = useState('tasks')
  const navigate = useNavigate()
  // Dummy data
  const tasks = [
    { id: 1, title: 'Design landing page', status: 'In Progress' },
    { id: 2, title: 'Integrate Discord bot', status: 'Pending' },
    { id: 3, title: 'Set up Firebase', status: 'Completed' },
    { id: 4, title: 'Write documentation', status: 'In Progress' },
  ]
  // Team members with levels and completed tasks
  const team = [
    { name: 'Red', role: 'Developer', avatar: amogus32Dance, level: 1, completed: 3 },
    { name: 'Green', role: 'Designer', avatar: amogus16, level: 2, completed: 7 },
    { name: 'Blue', role: 'Bot Master', avatar: amogus8Flip, level: 1, completed: 2 },
  ]
  // Team Amogus progress is sum of all completed
  const teamTotal = team.reduce((sum, m) => sum + m.completed, 0)
  const teamLevel = Math.floor(teamTotal / 5) + 1
  const teamGrowth = Math.min(100, (teamTotal % 5) * 20)
  const performance = {
    completed: 12,
    total: 20,
    streak: 5,
    growth: 60, // percent
  }
  // Fake calendar data
  const calendar = [
    { day: 'Mon', task: 'Design landing page' },
    { day: 'Tue', task: 'Integrate Discord bot' },
    { day: 'Wed', task: 'Set up Firebase' },
    { day: 'Thu', task: 'Write documentation' },
    { day: 'Fri', task: 'Review & deploy' },
  ]
  return (
    <div className="dashboard-layout dashboard-bg">
      <aside className="dashboard-sidebar wide-sidebar">
        <div className="sidebar-logo-row">
          <button className="back-btn" onClick={() => navigate('/')} title="Back to Home">←</button>
          <img src={logo} alt="Crewmate Logo" className="sidebar-logo" />
          <span className="sidebar-title">DASHBOARD</span>
        </div>
        <nav className="sidebar-nav">
          <button className={`sidebar-link${tab === 'tasks' ? ' active' : ''}`} onClick={() => setTab('tasks')}>Tasks</button>
          <button className={`sidebar-link${tab === 'performance' ? ' active' : ''}`} onClick={() => setTab('performance')}>Performance</button>
          <button className={`sidebar-link${tab === 'team' ? ' active' : ''}`} onClick={() => setTab('team')}>Team</button>
        </nav>
      </aside>
      <main className="dashboard-main-area dashboard-main-bg dashboard-main-flex">
        <header className="dashboard-header dashboard-header-bg">
          <input className="dashboard-search" placeholder="Search tasks, team, or performance..." />
          <span className="dashboard-title">Welcome, Crew Member!</span>
        </header>
        <section className="dashboard-progress-section dashboard-card no-radius">
          <div className="progress-bar-label">Team Amogus (Lv.{teamLevel})</div>
          <div className="growing-amogus-bar">
            <div className="growing-amogus-progress">
              <img src={amogus32Dance} alt="Team Amogus" className="growing-amogus-img" style={{ height: 64 + teamGrowth, maxHeight: 160, transition: 'height 0.5s' }} />
              <div className="progress-bar-outer styled-progress-bar no-radius">
                <div className="progress-bar-inner styled-progress-bar-inner" style={{ width: `${teamGrowth}%` }}></div>
              </div>
            </div>
            <span className="growth-label">{teamTotal} tasks complete (Lv.{teamLevel})</span>
          </div>
          <div className="dashboard-tabs compact-tabs">
            <button className={`tab${tab === 'tasks' ? ' active' : ''}`} onClick={() => setTab('tasks')}>Tasks</button>
            <button className={`tab${tab === 'performance' ? ' active' : ''}`} onClick={() => setTab('performance')}>Performance</button>
            <button className={`tab${tab === 'team' ? ' active' : ''}`} onClick={() => setTab('team')}>Team</button>
          </div>
          <div className="dashboard-tab-content">
            {tab === 'tasks' && (
              <div className="dashboard-tasks-columns">
                <div className="task-column dashboard-card no-radius">
                  <div className="column-title">In Progress</div>
                  {tasks.filter(t => t.status === 'In Progress').map(t => (
                    <div className="task-card" key={t.id}>{t.title}</div>
                  ))}
                </div>
                <div className="task-column dashboard-card no-radius">
                  <div className="column-title">Pending</div>
                  {tasks.filter(t => t.status === 'Pending').map(t => (
                    <div className="task-card" key={t.id}>{t.title}</div>
                  ))}
                </div>
                <div className="task-column dashboard-card no-radius">
                  <div className="column-title">Completed</div>
                  {tasks.filter(t => t.status === 'Completed').map(t => (
                    <div className="task-card completed" key={t.id}>{t.title}</div>
                  ))}
                </div>
              </div>
            )}
            {tab === 'performance' && (
              <div className="dashboard-performance dashboard-card no-radius">
                <div className="performance-metric">Tasks Completed: <strong>{performance.completed}</strong></div>
                <div className="performance-metric">Total Tasks: <strong>{performance.total}</strong></div>
                <div className="performance-metric">Streak: <strong>{performance.streak} days</strong></div>
                <div className="performance-metric">Growth: <strong>{performance.growth}%</strong></div>
              </div>
            )}
            {tab === 'team' && (
              <div className="dashboard-team dashboard-card no-radius">
                {team.map(member => (
                  <div className="team-member no-radius" key={member.name}>
                    <img src={member.avatar} alt={member.name} className="team-avatar" style={{ height: 48 + member.completed * 6, maxHeight: 120, transition: 'height 0.5s' }} />
                    <div className="team-info">
                      <div className="team-name">{member.name} (Lv.{member.level})</div>
                      <div className="team-role">{member.role}</div>
                      <div className="team-tasks">Tasks: {member.completed}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
      <aside className="dashboard-rightbar dashboard-card dashboard-calendar-bg no-radius">
        <div className="rightbar-header">
          <span className="rightbar-title">Calendar</span>
        </div>
        <div className="rightbar-calendar-list">
          {calendar.map((item, idx) => (
            <div className="calendar-item no-radius" key={idx}>
              <span className="calendar-day">{item.day}</span>
              <span className="calendar-task">{item.task}</span>
            </div>
          ))}
        </div>
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
          <PricingSection />
          <Footer />
        </>
      } />
      <Route path="/dashboard" element={<DashboardPage />} />
    </Routes>
  )
}

export default App

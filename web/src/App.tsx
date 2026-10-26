import { useEffect, useState, type FormEvent } from 'react';
import { Activity, Bot, BriefcaseBusiness, CalendarCheck, CheckCheck, CircleHelp, ClipboardList, FileText, LayoutDashboard, LogOut, MessageCircle, Search, Settings2, ShieldCheck, Users, Workflow, Bell, Send } from 'lucide-react';
import { apiGet, apiPost, type CurrentUser, type Organization } from './api';

type TokenPair = { access: string; refresh: string };
type FeedPost = { id: string; author_name: string; post_type: string; body: string; created_at: string; reaction_count: number };
type Employee = { id: string; user_id: string; display_name: string; employee_code: string; job_title: string; department: string };
type DirectMessage = { id: string; sender: string; sender_name: string; recipient: string; recipient_name: string; body: string; sent_at: string; read_at: string | null };
type Notice = { id: string; kind: string; title: string; body: string; created_at: string; read_at: string | null };
const nav = [
  { label: 'Overview', icon: LayoutDashboard }, { label: 'Company feed', icon: MessageCircle },
  { label: 'My work', icon: CheckCheck }, { label: 'Projects & clients', icon: BriefcaseBusiness },
  { label: 'People', icon: Users }, { label: 'Messages', icon: Send }, { label: 'Notifications', icon: Bell },
  { label: 'EOD reports', icon: FileText }, { label: 'HR self-service', icon: CalendarCheck },
  { label: 'AI workforce', icon: Bot }, { label: 'Approvals', icon: ShieldCheck },
  { label: 'Integrations', icon: Workflow }, { label: 'Administration', icon: Settings2 },
];

export default function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [active, setActive] = useState('Overview');
  const [posts, setPosts] = useState<FeedPost[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [messages, setMessages] = useState<DirectMessage[]>([]);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [recipient, setRecipient] = useState('');
  const [messageBody, setMessageBody] = useState('');
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [sectionLoading, setSectionLoading] = useState(false);
  const [apiState, setApiState] = useState<'NOT_CONFIGURED' | 'READY' | 'UNAVAILABLE'>('READY');

  async function loadWorkspace(access: string, org: Organization) {
    try {
      const feed = await apiGet<FeedPost[]>('/feed/posts/', access, org.id);
      setPosts(Array.isArray(feed) ? feed : []);
      setApiState('READY');
    } catch (e) {
      setApiState('UNAVAILABLE');
      setError(e instanceof Error ? e.message : 'Unable to load workspace.');
    }
  }

  async function login(e: FormEvent) {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      const pair = await apiPost<TokenPair>('/auth/token/', { username, password });
      const me = await apiGet<CurrentUser>('/me/', pair.access);
      setToken(pair.access); setUser(me); setPassword('');
      const org = me.organizations[0];
      if (org) { setOrganization(org); await loadWorkspace(pair.access, org); }
      else setError('Your account has no active agency membership. Ask an administrator to assign one.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign-in failed.');
    } finally { setLoading(false); }
  }

  useEffect(() => {
    if (!token || !organization) return;
    let cancelled = false;
    async function loadSection() {
      setSectionLoading(true); setError('');
      try {
        if (active === 'People') {
          const data = await apiGet<Employee[]>('/employees/', token!, organization!.id);
          if (!cancelled) setEmployees(Array.isArray(data) ? data : []);
        } else if (active === 'Messages') {
          const data = await apiGet<DirectMessage[]>('/employees/messages/', token!, organization!.id);
          if (!cancelled) setMessages(Array.isArray(data) ? data : []);
        } else if (active === 'Notifications') {
          const data = await apiGet<Notice[]>('/employees/notifications/', token!, organization!.id);
          if (!cancelled) setNotices(Array.isArray(data) ? data : []);
        } else if (active === 'Company feed') {
          await loadWorkspace(token!, organization!);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load this workspace.');
      } finally { if (!cancelled) setSectionLoading(false); }
    }
    void loadSection();
    return () => { cancelled = true; };
  }, [token, organization?.id, active]);

  function signOut() {
    setToken(null); setUser(null); setOrganization(null); setPosts([]); setEmployees([]); setMessages([]); setNotices([]); setPassword(''); setError('');
  }

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!token || !organization || !recipient || !messageBody.trim()) return;
    setError('');
    try {
      await apiPost<DirectMessage>('/employees/messages/', { recipient, body: messageBody.trim() }, token, organization.id);
      setMessageBody('');
      setMessages(await apiGet<DirectMessage[]>('/employees/messages/', token, organization.id));
    } catch (err) { setError(err instanceof Error ? err.message : 'Message could not be sent.'); }
  }

  async function markRead(notice: Notice) {
    if (!token || !organization || notice.read_at) return;
    try {
      const updated = await apiPost<Notice>(`/employees/notifications/${notice.id}/read/`, {}, token, organization.id);
      setNotices(current => current.map(item => item.id === updated.id ? updated : item));
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not mark notification read.'); }
  }

  if (!token || !user) return <main className="auth-wrap"><form className="auth-card" onSubmit={login}>
    <div className="brand">ALIENHOUSE <span>OS</span></div><div className="eyebrow">Agency operating system</div>
    <h1>Sign in to your workspace</h1><p className="muted">Use your agency account. Access is checked by the server.</p>
    <label>Username<input autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} required /></label>
    <label>Password<input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
    {error && <div className="error" role="alert">{error}</div>}
    <button className="primary" type="submit" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button>
    <p className="muted small">API: {import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'}</p>
  </form></main>;

  const filteredEmployees = employees.filter(employee => `${employee.display_name} ${employee.employee_code} ${employee.department} ${employee.job_title}`.toLowerCase().includes(search.toLowerCase()));
  const sectionContent = active === 'Overview' ? <div className="grid">
    <section className="panel"><h3>My workspace</h3><div className="metric">—</div><div className="muted">Tasks load when the task workspace is connected.</div></section>
    <section className="panel"><h3>Delivery health</h3><div className="metric">—</div><div className="muted">No verified metric loaded.</div></section>
    <section className="panel"><h3>Pending approvals</h3><div className="metric">—</div><div className="muted">Connect the approval queue to load counts.</div></section>
    <section className="panel wide"><h3>Company feed</h3>{posts.length ? <div className="feedbox">{posts.map(post => <article className="feedpost" key={post.id}><strong>{post.author_name}</strong><div className="muted" style={{fontSize:12, marginTop:4}}>{post.post_type} · {new Date(post.created_at).toLocaleString()}</div><p>{post.body}</p><span className="muted">{post.reaction_count} reactions</span></article>)}</div> : <p className="muted">No accessible posts were returned by the API, or the feed has not been populated.</p>}</section>
    <section className="panel"><h3>Quick actions</h3><div className="rows">{['Draft EOD report','Create a task','Request leave','Ask AI assistant'].map(item => <div className="rowitem" key={item}><span>{item}</span><span className="muted">→</span></div>)}</div></section>
  </div> : active === 'People' ? <section className="panel"><h3>Employee directory</h3><label className="searchbox"><Search size={16}/><input aria-label="Search people" placeholder="Search name, role, department or employee code" value={search} onChange={e => setSearch(e.target.value)} /></label>{sectionLoading ? <p className="muted">Loading directory…</p> : filteredEmployees.length ? <div className="rows">{filteredEmployees.map(employee => <article className="rowitem" key={employee.id}><div><strong>{employee.display_name}</strong><div className="muted">{employee.job_title || 'Role not set'} · {employee.department || 'Department not set'} · {employee.employee_code}</div></div></article>)}</div> : <p className="muted">No active employee profiles found for this organization.</p>}</section>
  : active === 'Messages' ? <section className="panel"><h3>Direct messages</h3><form onSubmit={sendMessage} className="message-form"><label>Recipient<select value={recipient} onChange={e => setRecipient(e.target.value)} required><option value="">Choose a colleague</option>{employees.map(employee => <option key={employee.user_id} value={employee.user_id}>{employee.display_name} — {employee.department}</option>)}</select></label><label>Message<textarea value={messageBody} onChange={e => setMessageBody(e.target.value)} required maxLength={10000} placeholder="Write a work-related message…" /></label><button className="primary" type="submit"><Send size={15}/> Send message</button></form>{sectionLoading ? <p className="muted">Loading messages…</p> : messages.length ? <div className="rows">{messages.map(message => <article className="feedpost" key={message.id}><strong>{message.sender_name} → {message.recipient_name}</strong><div className="muted small">{new Date(message.sent_at).toLocaleString()}</div><p>{message.body}</p></article>)}</div> : <p className="muted">No messages in this organization yet.</p>}</section>
  : active === 'Notifications' ? <section className="panel"><h3>Notifications</h3>{sectionLoading ? <p className="muted">Loading notifications…</p> : notices.length ? <div className="rows">{notices.map(notice => <article className="rowitem" key={notice.id}><div><strong>{notice.title}</strong><div className="muted">{notice.kind} · {new Date(notice.created_at).toLocaleString()}</div><p>{notice.body}</p></div>{!notice.read_at && <button onClick={() => void markRead(notice)}>Mark read</button>}</article>)}</div> : <p className="muted">No notifications are available.</p>}</section>
  : active === 'Company feed' ? <section className="panel"><h3>Company feed</h3>{posts.map(post => <article className="feedpost" key={post.id}><strong>{post.author_name}</strong><div className="muted small">{post.post_type} · {new Date(post.created_at).toLocaleString()}</div><p>{post.body}</p><span className="muted">{post.reaction_count} reactions</span></article>)}{!posts.length && <p className="muted">No accessible posts found.</p>}</section>
  : <section className="panel"><h3>{active}</h3><p className="muted">This workspace requires its domain-specific API journey to be completed. Data is not simulated or inferred.</p><div className="rowitem"><Search size={16}/><span>Search and filtering use authorized server endpoints.</span></div><div className="rowitem"><ClipboardList size={16}/><span>Records are scoped to the active organization.</span></div><div className="rowitem"><CircleHelp size={16}/><span>Disconnected integrations display explicit status.</span></div></section>;

  return <div className="shell"><aside className="sidebar"><div className="brand">ALIENHOUSE <span>OS</span></div><div className="nav">{nav.map(({label, icon: Icon}) => <button key={label} className={active === label ? 'active' : ''} onClick={() => { setActive(label); setSearch(''); }}><Icon size={17} style={{verticalAlign:'-3px', marginRight:10}}/>{label}</button>)}</div><div className="notice">Signed in as <strong>{user.username}</strong><br/><span className="muted">{organization?.name ?? 'No active organization'}</span><button className="logout" onClick={signOut}><LogOut size={14}/> Sign out</button></div></aside>
    <main className="main"><div className="header"><div><div className="eyebrow">Agency operating system</div><h1>{active}</h1><div className="muted">One place for people, client work and verified execution.</div></div><div className="pill"><span className="dot"/>{apiState}</div></div>
    {user.organizations.length > 1 && <label className="org-select">Agency<select value={organization?.id ?? ''} onChange={e => setOrganization(user.organizations.find(org => org.id === e.target.value) ?? null)}>{user.organizations.map(org => <option key={org.id} value={org.id}>{org.name}</option>)}</select></label>}
    {error && <div className="error" role="alert">{error}</div>}{sectionContent}
    <div className="notice"><Activity size={15} style={{verticalAlign:'-3px', marginRight:8}}/>Metrics use an em dash until a real source is connected; the UI does not substitute zero for unavailable data.</div></main></div>;
}

import { useEffect, useState, type FormEvent } from 'react';
import { Activity, Bot, BriefcaseBusiness, CalendarCheck, CheckCheck, CircleHelp, ClipboardList, FileText, LayoutDashboard, LogOut, MessageCircle, Search, Settings2, ShieldCheck, Users, Workflow, Bell, Send } from 'lucide-react';
import { apiGet, apiPost, type CurrentUser, type Organization } from './api';

type TokenPair = { access: string; refresh: string };
type FeedPost = { id: string; author_name: string; post_type: string; body: string; created_at: string; reaction_count: number };
type Employee = { id: string; user_id: string; display_name: string; employee_code: string; job_title: string; department: string };
type DirectMessage = { id: string; sender: string; sender_name: string; recipient: string; recipient_name: string; body: string; sent_at: string; read_at: string | null };
type Notice = { id: string; kind: string; title: string; body: string; created_at: string; read_at: string | null };
type EODReport = { id: string; report_date: string; status: string; completed_work: string; in_progress: string; blockers: string; next_day_priorities: string; evidence: Array<{title:string;type:string;reference:string}>; version: number; review_note: string };
type LeaveRequest = { id: string; leave_type: string; start_date: string; end_date: string; reason: string; status: string };
type AttendanceEntry = { id: string; started_at: string; ended_at: string | null; status: string; note: string };
type ClientAccount = { id: string; name: string; status: string; account_owner: string | null; created_at: string };
type AgencyProject = { id: string; client: string | null; name: string; service_line: string; description: string; status: string; due_date: string | null; created_at: string };
const nav = [
  { label: 'Overview', icon: LayoutDashboard }, { label: 'Company feed', icon: MessageCircle },
  { label: 'My work', icon: CheckCheck }, { label: 'Projects & clients', icon: BriefcaseBusiness },
  { label: 'People', icon: Users }, { label: 'Messages', icon: Send }, { label: 'Notifications', icon: Bell },
  { label: 'EOD reports', icon: FileText }, { label: 'HR self-service', icon: CalendarCheck },
  { label: 'AI workforce', icon: Bot }, { label: 'Approvals', icon: ShieldCheck },
  { label: 'Integrations', icon: Workflow }, { label: 'Administration', icon: Settings2 },
];

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
const DJANGO_ADMIN_URL = API_BASE.replace(/\/api\/v1\/?$/, '/admin/');

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
  const [eodReports, setEodReports] = useState<EODReport[]>([]);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [attendanceEntries, setAttendanceEntries] = useState<AttendanceEntry[]>([]);
  const [clients, setClients] = useState<ClientAccount[]>([]);
  const [projects, setProjects] = useState<AgencyProject[]>([]);
  const [clientName, setClientName] = useState('');
  const [projectName, setProjectName] = useState('');
  const [projectServiceLine, setProjectServiceLine] = useState('SOFTWARE');
  const [projectClientId, setProjectClientId] = useState('');
  const [projectDueDate, setProjectDueDate] = useState('');
  const [eodDate, setEodDate] = useState(new Date().toISOString().slice(0, 10));
  const [eodCompleted, setEodCompleted] = useState('');
  const [eodInProgress, setEodInProgress] = useState('');
  const [eodBlockers, setEodBlockers] = useState('');
  const [eodNext, setEodNext] = useState('');
  const [leaveType, setLeaveType] = useState('CASUAL');
  const [leaveStart, setLeaveStart] = useState('');
  const [leaveEnd, setLeaveEnd] = useState('');
  const [leaveReason, setLeaveReason] = useState('');
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
          const [data, people] = await Promise.all([
            apiGet<DirectMessage[]>('/employees/messages/', token!, organization!.id),
            apiGet<Employee[]>('/employees/', token!, organization!.id),
          ]);
          if (!cancelled) { setMessages(Array.isArray(data) ? data : []); setEmployees(Array.isArray(people) ? people : []); }
        } else if (active === 'EOD reports') {
          const data = await apiGet<EODReport[]>('/eod/reports/', token!, organization!.id);
          if (!cancelled) setEodReports(Array.isArray(data) ? data : []);
        } else if (active === 'HR self-service') {
          const [attendance, leave] = await Promise.all([
            apiGet<AttendanceEntry[]>('/hr/attendance/', token!, organization!.id),
            apiGet<LeaveRequest[]>('/hr/leave/', token!, organization!.id),
          ]);
          if (!cancelled) { setAttendanceEntries(Array.isArray(attendance) ? attendance : []); setLeaveRequests(Array.isArray(leave) ? leave : []); }
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

  async function createClient(event: FormEvent) {
    event.preventDefault();
    if (!token || !organization) return;
    try {
      const created = await apiPost<ClientAccount>('/delivery/clients/', { name: clientName.trim() }, token, organization.id);
      setClients(current => [created, ...current]);
      setClientName('');
    } catch (err) { setError(err instanceof Error ? err.message : 'Client could not be created.'); }
  }

  async function createProject(event: FormEvent) {
    event.preventDefault();
    if (!token || !organization) return;
    try {
      const payload: Record<string, string | null> = {
        name: projectName.trim(),
        service_line: projectServiceLine,
        client: projectClientId || null,
        due_date: projectDueDate || null,
      };
      const created = await apiPost<AgencyProject>('/delivery/projects/', payload, token, organization.id);
      setProjects(current => [created, ...current]);
      setProjectName('');
      setProjectDueDate('');
      setProjectClientId('');
    } catch (err) { setError(err instanceof Error ? err.message : 'Project could not be created.'); }
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

  async function createEod(event: FormEvent) {
    event.preventDefault();
    if (!token || !organization) return;
    try {
      const report = await apiPost<EODReport>('/eod/reports/', { report_date: eodDate, completed_work: eodCompleted, in_progress: eodInProgress, blockers: eodBlockers, next_day_priorities: eodNext, evidence: [] }, token, organization.id);
      setEodReports(current => [report, ...current]);
      setEodCompleted(''); setEodInProgress(''); setEodBlockers(''); setEodNext('');
    } catch (err) { setError(err instanceof Error ? err.message : 'EOD report could not be saved.'); }
  }

  async function submitEod(report: EODReport) {
    if (!token || !organization || !['DRAFT','NEEDS_CHANGES'].includes(report.status)) return;
    try {
      const updated = await apiPost<EODReport>('/eod/reports/' + report.id + '/submit/', {}, token, organization.id);
      setEodReports(current => current.map(item => item.id === updated.id ? updated : item));
    } catch (err) { setError(err instanceof Error ? err.message : 'EOD report could not be submitted.'); }
  }

  async function attendanceAction(action: 'check_in' | 'check_out') {
    if (!token || !organization) return;
    try {
      await apiPost<AttendanceEntry>('/hr/attendance/action/', { action }, token, organization.id);
      setAttendanceEntries(await apiGet<AttendanceEntry[]>('/hr/attendance/', token, organization.id));
    } catch (err) { setError(err instanceof Error ? err.message : 'Attendance action failed.'); }
  }

  async function createLeave(event: FormEvent) {
    event.preventDefault();
    if (!token || !organization) return;
    try {
      const created = await apiPost<LeaveRequest>('/hr/leave/', { leave_type: leaveType, start_date: leaveStart, end_date: leaveEnd, reason: leaveReason }, token, organization.id);
      setLeaveRequests(current => [created, ...current]); setLeaveStart(''); setLeaveEnd(''); setLeaveReason('');
    } catch (err) { setError(err instanceof Error ? err.message : 'Leave request could not be submitted.'); }
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
  : active === 'Projects & clients' ? <div className="grid">
    <section className="panel"><h3>Client onboarding</h3><p className="muted">Create an agency client record. Client-specific intake forms, contracts and approvals are not yet implemented.</p><form className="message-form" onSubmit={createClient}><label>Client / company name<input value={clientName} onChange={e => setClientName(e.target.value)} required maxLength={200} placeholder="Company name" /></label><button className="primary" type="submit">Create client</button></form><h3>Clients</h3>{sectionLoading ? <p className="muted">Loading clients…</p> : clients.length ? <div className="rows">{clients.map(client => <article className="rowitem" key={client.id}><div><strong>{client.name}</strong><div className="muted">{client.status}</div></div></article>)}</div> : <p className="muted">No clients are available for this organization.</p>}</section>
    <section className="panel"><h3>Project setup</h3><form className="message-form" onSubmit={createProject}><label>Project name<input value={projectName} onChange={e => setProjectName(e.target.value)} required maxLength={200} /></label><label>Service line<select value={projectServiceLine} onChange={e => setProjectServiceLine(e.target.value)}><option value="SOFTWARE">Software development</option><option value="AI">AI & automation</option><option value="MARKETING">Digital marketing</option><option value="CREATIVE">Creative services</option><option value="CONSULTING">Consulting</option><option value="OTHER">Other</option></select></label><label>Client<select value={projectClientId} onChange={e => setProjectClientId(e.target.value)}><option value="">No client linked</option>{clients.map(client => <option key={client.id} value={client.id}>{client.name}</option>)}</select></label><label>Due date<input type="date" value={projectDueDate} onChange={e => setProjectDueDate(e.target.value)} /></label><button className="primary" type="submit">Create project</button></form><h3>Projects</h3>{sectionLoading ? <p className="muted">Loading projects…</p> : projects.length ? <div className="rows">{projects.map(project => <article className="rowitem" key={project.id}><div><strong>{project.name}</strong><div className="muted">{project.service_line} · {project.status}{project.due_date ? ` · Due ${project.due_date}` : ''}</div><div className="muted small">{clients.find(client => client.id === project.client)?.name ?? 'No client linked'}</div></div></article>)}</div> : <p className="muted">No projects are available for this organization.</p>}</section>
  </div>
  : active === 'Messages' ? <section className="panel"><h3>Direct messages</h3><form onSubmit={sendMessage} className="message-form"><label>Recipient<select value={recipient} onChange={e => setRecipient(e.target.value)} required><option value="">Choose a colleague</option>{employees.map(employee => <option key={employee.user_id} value={employee.user_id}>{employee.display_name} — {employee.department}</option>)}</select></label><label>Message<textarea value={messageBody} onChange={e => setMessageBody(e.target.value)} required maxLength={10000} placeholder="Write a work-related message…" /></label><button className="primary" type="submit"><Send size={15}/> Send message</button></form>{sectionLoading ? <p className="muted">Loading messages…</p> : messages.length ? <div className="rows">{messages.map(message => <article className="feedpost" key={message.id}><strong>{message.sender_name} → {message.recipient_name}</strong><div className="muted small">{new Date(message.sent_at).toLocaleString()}</div><p>{message.body}</p></article>)}</div> : <p className="muted">No messages in this organization yet.</p>}</section>
  : active === 'EOD reports' ? <div className="grid"><section className="panel wide"><h3>Create daily report</h3><form className="message-form" onSubmit={createEod}><label>Report date<input type="date" value={eodDate} onChange={e => setEodDate(e.target.value)} required /></label><label>Completed work<textarea value={eodCompleted} onChange={e => setEodCompleted(e.target.value)} maxLength={10000} required /></label><label>In progress<textarea value={eodInProgress} onChange={e => setEodInProgress(e.target.value)} maxLength={10000} /></label><label>Blockers<textarea value={eodBlockers} onChange={e => setEodBlockers(e.target.value)} maxLength={10000} /></label><label>Next-day priorities<textarea value={eodNext} onChange={e => setEodNext(e.target.value)} maxLength={10000} /></label><button className="primary" type="submit">Save draft</button></form></section><section className="panel wide"><h3>My EOD history</h3>{eodReports.map(report => <article className="feedpost" key={report.id}><strong>{report.report_date} · {report.status} · v{report.version}</strong><p>{report.completed_work}</p>{report.review_note && <p className="muted">Manager note: {report.review_note}</p>}{['DRAFT','NEEDS_CHANGES'].includes(report.status) && <button onClick={() => void submitEod(report)}>Submit for review</button>}</article>)}{!eodReports.length && <p className="muted">No reports returned by the API.</p>}</section></div>
  : active === 'HR self-service' ? <div className="grid"><section className="panel"><h3>Attendance</h3><div className="actions"><button className="primary" onClick={() => void attendanceAction('check_in')}>Check in</button><button onClick={() => void attendanceAction('check_out')}>Check out</button></div>{attendanceEntries.map(entry => <article className="feedpost" key={entry.id}><strong>{entry.status}</strong><div>{new Date(entry.started_at).toLocaleString()} — {entry.ended_at ? new Date(entry.ended_at).toLocaleString() : 'Open session'}</div></article>)}</section><section className="panel"><h3>Request leave</h3><form className="message-form" onSubmit={createLeave}><label>Leave type<select value={leaveType} onChange={e => setLeaveType(e.target.value)}><option value="CASUAL">Casual</option><option value="SICK">Sick</option><option value="ANNUAL">Annual</option><option value="UNPAID">Unpaid</option></select></label><label>Start date<input type="date" value={leaveStart} onChange={e => setLeaveStart(e.target.value)} required /></label><label>End date<input type="date" value={leaveEnd} onChange={e => setLeaveEnd(e.target.value)} required /></label><label>Reason<textarea value={leaveReason} onChange={e => setLeaveReason(e.target.value)} maxLength={3000} /></label><button className="primary" type="submit">Submit leave request</button></form><h3>My requests</h3>{leaveRequests.map(item => <article className="feedpost" key={item.id}><strong>{item.leave_type} · {item.status}</strong><div>{item.start_date} to {item.end_date}</div><p>{item.reason}</p></article>)}</section></div>
  : active === 'Administration' ? <div className="grid">
    <section className="panel wide"><h3>Django administration</h3><p>Use Django’s built-in admin site for system-level management of users, agency memberships, employee records, CRM, delivery, HR requests, approvals, EOD history, integration records and audit events.</p><p className="muted">This opens the backend admin login in a separate page. Access is controlled by Django staff permissions; API login alone does not grant admin access.</p><div className="actions"><a className="primary" href={DJANGO_ADMIN_URL} target="_blank" rel="noreferrer">Open Django Admin ↗</a></div></section>
    <section className="panel"><h3>Access and safety</h3><ul><li>Only authorized Django staff accounts can sign in.</li><li>Audit events and EOD revision history are read-only.</li><li>Approval decisions should use the application approval workflow, not direct database edits.</li><li>Review staff and model permissions before production access.</li></ul></section>
  </div>
  : active === 'Notifications' ? <section className="panel"><h3>Notifications</h3>{sectionLoading ? <p className="muted">Loading notifications…</p> : notices.length ? <div className="rows">{notices.map(notice => <article className="rowitem" key={notice.id}><div><strong>{notice.title}</strong><div className="muted">{notice.kind} · {new Date(notice.created_at).toLocaleString()}</div><p>{notice.body}</p></div>{!notice.read_at && <button onClick={() => void markRead(notice)}>Mark read</button>}</article>)}</div> : <p className="muted">No notifications are available.</p>}</section>
  : active === 'Company feed' ? <section className="panel"><h3>Company feed</h3>{posts.map(post => <article className="feedpost" key={post.id}><strong>{post.author_name}</strong><div className="muted small">{post.post_type} · {new Date(post.created_at).toLocaleString()}</div><p>{post.body}</p><span className="muted">{post.reaction_count} reactions</span></article>)}{!posts.length && <p className="muted">No accessible posts found.</p>}</section>
  : <section className="panel"><h3>{active}</h3><p className="muted">This workspace requires its domain-specific API journey to be completed. Data is not simulated or inferred.</p><div className="rowitem"><Search size={16}/><span>Search and filtering use authorized server endpoints.</span></div><div className="rowitem"><ClipboardList size={16}/><span>Records are scoped to the active organization.</span></div><div className="rowitem"><CircleHelp size={16}/><span>Disconnected integrations display explicit status.</span></div></section>;

  return <div className="shell"><aside className="sidebar"><div className="brand">ALIENHOUSE <span>OS</span></div><div className="nav">{nav.map(({label, icon: Icon}) => <button key={label} className={active === label ? 'active' : ''} onClick={() => { setActive(label); setSearch(''); }}><Icon size={17} style={{verticalAlign:'-3px', marginRight:10}}/>{label}</button>)}</div><div className="notice">Signed in as <strong>{user.username}</strong><br/><span className="muted">{organization?.name ?? 'No active organization'}</span><button className="logout" onClick={signOut}><LogOut size={14}/> Sign out</button></div></aside>
    <main className="main"><div className="header"><div><div className="eyebrow">Agency operating system</div><h1>{active}</h1><div className="muted">One place for people, client work and verified execution.</div></div><div className="pill"><span className="dot"/>{apiState}</div></div>
    {user.organizations.length > 1 && <label className="org-select">Agency<select value={organization?.id ?? ''} onChange={e => setOrganization(user.organizations.find(org => org.id === e.target.value) ?? null)}>{user.organizations.map(org => <option key={org.id} value={org.id}>{org.name}</option>)}</select></label>}
    {error && <div className="error" role="alert">{error}</div>}{sectionContent}
    <div className="notice"><Activity size={15} style={{verticalAlign:'-3px', marginRight:8}}/>Metrics use an em dash until a real source is connected; the UI does not substitute zero for unavailable data.</div></main></div>;
}

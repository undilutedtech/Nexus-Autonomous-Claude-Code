/**
 * Nexus API Client
 * =================
 *
 * HTTP client for communicating with the Nexus backend.
 */

const API_BASE = '/api'

interface FetchOptions extends RequestInit {
  skipAuth?: boolean
}

/**
 * Get the stored auth token.
 */
export function getAuthToken(): string | null {
  return localStorage.getItem('nexus_token')
}

/**
 * Set the auth token.
 */
export function setAuthToken(token: string): void {
  localStorage.setItem('nexus_token', token)
}

/**
 * Clear the auth token.
 */
export function clearAuthToken(): void {
  localStorage.removeItem('nexus_token')
}

/**
 * Fetch JSON from the API with authentication.
 */
export async function fetchJSON<T>(url: string, options: FetchOptions = {}): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((fetchOptions.headers as Record<string, string>) || {}),
  }

  // Add auth header if we have a token and not skipping auth
  if (!skipAuth) {
    const token = getAuthToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...fetchOptions,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    const err = new Error(error.detail || `HTTP ${response.status}`) as Error & {
      status: number
      mfaRequired?: boolean
    }
    err.status = response.status

    // Check for MFA required
    if (response.headers.get('X-MFA-Required') === 'true') {
      err.mfaRequired = true
    }

    throw err
  }

  return response.json()
}

// ============================================================================
// Auth API
// ============================================================================

export interface UserResponse {
  id: number
  email: string
  username: string
  full_name: string | null
  avatar_url: string | null
  bio: string | null
  mfa_enabled: boolean
  created_at: string
  last_login: string | null
  settings: Record<string, unknown>
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserResponse
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface LoginData {
  email_or_username: string
  password: string
  mfa_code?: string
}

export interface ProfileUpdate {
  full_name?: string
  bio?: string
  avatar_url?: string
}

export interface PasswordChange {
  current_password: string
  new_password: string
}

export interface MFASetupResponse {
  secret: string
  qr_code: string
}

export interface MFAEnableData {
  secret: string
  code: string
}

export interface MFAVerifyData {
  code: string
}

// Auth endpoints
export const authAPI = {
  register: (data: RegisterData): Promise<TokenResponse> =>
    fetchJSON('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true,
    }),

  login: (data: LoginData): Promise<TokenResponse> =>
    fetchJSON('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true,
    }),

  getMe: (): Promise<UserResponse> => fetchJSON('/auth/me'),

  updateProfile: (data: ProfileUpdate): Promise<UserResponse> =>
    fetchJSON('/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  changePassword: (data: PasswordChange): Promise<{ success: boolean; message: string }> =>
    fetchJSON('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateSettings: (settings: Record<string, unknown>): Promise<UserResponse> =>
    fetchJSON('/auth/settings', {
      method: 'PATCH',
      body: JSON.stringify({ settings }),
    }),

  // MFA
  setupMFA: (): Promise<MFASetupResponse> =>
    fetchJSON('/auth/mfa/setup', { method: 'POST' }),

  enableMFA: (data: MFAEnableData): Promise<{ success: boolean; message: string }> =>
    fetchJSON('/auth/mfa/enable', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  disableMFA: (data: MFAVerifyData): Promise<{ success: boolean; message: string }> =>
    fetchJSON('/auth/mfa/disable', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  verifyMFA: (data: MFAVerifyData): Promise<{ valid: boolean }> =>
    fetchJSON('/auth/mfa/verify', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// ============================================================================
// Projects API (for later use)
// ============================================================================

export interface ProjectStats {
  passing: number
  in_progress: number
  total: number
  percentage: number
}

export interface ProjectSummary {
  name: string
  path: string
  has_spec: boolean
  stats: ProjectStats
  status?: 'active' | 'paused' | 'finished' | 'archived'
}

export interface ProjectCreate {
  name: string
  path: string
}

export interface ProjectOverviewStats {
  total_projects: number
  active_projects: number
  paused_projects: number
  finished_projects: number
  total_features: number
  total_passing: number
  overall_percentage: number
  // Active projects only stats
  active_features: number
  active_passing: number
  active_percentage: number
  active_in_progress: number
}

export interface ProjectStatusResponse {
  success: boolean
  project_name: string
  status: string
  message: string
}

export const projectsAPI = {
  list: (): Promise<ProjectSummary[]> => fetchJSON('/projects'),
  get: (name: string): Promise<ProjectSummary> => fetchJSON(`/projects/${encodeURIComponent(name)}`),
  create: (data: ProjectCreate): Promise<ProjectSummary> =>
    fetchJSON('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  delete: (name: string, deleteFiles: boolean = false): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(name)}?delete_files=${deleteFiles}`, {
      method: 'DELETE',
    }),

  // Project lifecycle
  getOverview: (): Promise<ProjectOverviewStats> => fetchJSON('/projects/overview'),
  getByStatus: (status: string): Promise<ProjectSummary[]> =>
    fetchJSON(`/projects/by-status/${status}`),
  pause: (name: string): Promise<ProjectStatusResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(name)}/pause`, { method: 'POST' }),
  resume: (name: string): Promise<ProjectStatusResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(name)}/resume`, { method: 'POST' }),
  finish: (name: string): Promise<ProjectStatusResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(name)}/finish`, { method: 'POST' }),
  restart: (name: string): Promise<ProjectStatusResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(name)}/restart`, { method: 'POST' }),
  reset: (name: string): Promise<ProjectStatusResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(name)}/reset`, { method: 'POST' }),
  archive: (name: string): Promise<ProjectStatusResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(name)}/archive`, { method: 'POST' }),
}

// ============================================================================
// Analytics API
// ============================================================================

export interface ProjectUsageBreakdown {
  name: string
  status: string
  sessions: number
  tokens: number
  cost_usd: number
  duration_hours: number
}

export interface AggregateUsageStats {
  total_projects_with_usage: number
  total_sessions: number
  total_input_tokens: number
  total_output_tokens: number
  total_cache_read_tokens: number
  total_cache_creation_tokens: number
  total_cost_usd: number
  total_duration_ms: number
  total_tokens: number
  avg_cost_per_project: number
  avg_sessions_per_project: number
  projects: ProjectUsageBreakdown[]
}

export const analyticsAPI = {
  getUsage: (): Promise<AggregateUsageStats> =>
    fetchJSON('/projects/analytics/usage'),
}

// ============================================================================
// Filesystem API
// ============================================================================

export interface DirectoryEntry {
  name: string
  path: string
  is_directory: boolean
  is_hidden: boolean
  size: number | null
  has_children: boolean
}

export interface DriveInfo {
  letter: string
  label: string
  available: boolean
}

export interface DirectoryListResponse {
  current_path: string
  parent_path: string | null
  entries: DirectoryEntry[]
  drives: DriveInfo[] | null
}

export interface PathValidationResponse {
  valid: boolean
  exists: boolean
  is_directory: boolean
  can_read: boolean
  can_write: boolean
  message: string
}

// ============================================================================
// Features API
// ============================================================================

export interface FeatureResponse {
  id: number
  priority: number
  category: string
  name: string
  description: string
  steps: string[]
  passes: boolean
  in_progress: boolean
}

export interface FeatureListResponse {
  pending: FeatureResponse[]
  in_progress: FeatureResponse[]
  done: FeatureResponse[]
}

export interface FeatureCreate {
  priority?: number
  category: string
  name: string
  description: string
  steps: string[]
}

export const featuresAPI = {
  list: (projectName: string): Promise<FeatureListResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/features`),

  get: (projectName: string, featureId: number): Promise<FeatureResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/features/${featureId}`),

  create: (projectName: string, data: FeatureCreate): Promise<FeatureResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/features`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  delete: (projectName: string, featureId: number): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/features/${featureId}`, {
      method: 'DELETE',
    }),

  skip: (projectName: string, featureId: number): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/features/${featureId}/skip`, {
      method: 'PATCH',
    }),

  clearInProgress: (projectName: string, featureId: number): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/features/${featureId}/clear-in-progress`, {
      method: 'PATCH',
    }),

  update: (projectName: string, featureId: number, data: Partial<FeatureCreate>): Promise<FeatureResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/features/${featureId}/update`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
}

// ============================================================================
// Agent API
// ============================================================================

export type AgentStatusType = 'stopped' | 'running' | 'paused' | 'crashed'

export type AgentPhaseType = 'idle' | 'initializing' | 'creating_features' | 'implementing' | 'complete'

export interface AgentPhaseInfo {
  phase: AgentPhaseType
  description: string
  estimate_min: number | null
  estimate_max: number | null
  progress: number | null
  features_total: number
  features_passing: number
  features_in_progress: number
}

export interface AgentStatus {
  status: AgentStatusType
  pid: number | null
  started_at: string | null
  yolo_mode: boolean
  model: string
  phase: AgentPhaseInfo | null
}

export interface AgentActionResponse {
  success: boolean
  status: AgentStatusType
  message: string
}

export interface AgentStartRequest {
  yolo_mode?: boolean
  model?: string
}

export const agentAPI = {
  getStatus: (projectName: string): Promise<AgentStatus> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agent/status`),

  start: (projectName: string, options?: AgentStartRequest): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agent/start`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  stop: (projectName: string): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agent/stop`, {
      method: 'POST',
    }),

  pause: (projectName: string): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agent/pause`, {
      method: 'POST',
    }),

  resume: (projectName: string): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agent/resume`, {
      method: 'POST',
    }),
}

export const filesystemAPI = {
  list: (path?: string, showHidden: boolean = false): Promise<DirectoryListResponse> => {
    const params = new URLSearchParams()
    if (path) params.set('path', path)
    if (showHidden) params.set('show_hidden', 'true')
    return fetchJSON(`/filesystem/list?${params.toString()}`)
  },

  getHome: (): Promise<{ path: string; display_path: string }> =>
    fetchJSON('/filesystem/home'),

  validate: (path: string): Promise<PathValidationResponse> =>
    fetchJSON(`/filesystem/validate?path=${encodeURIComponent(path)}`, { method: 'POST' }),

  createDirectory: (parentPath: string, name: string): Promise<{ success: boolean; path: string; message: string }> =>
    fetchJSON('/filesystem/create-directory', {
      method: 'POST',
      body: JSON.stringify({ parent_path: parentPath, name }),
    }),
}

// ============================================================================
// Multi-Agent API
// ============================================================================

export interface MultiAgentInfo {
  agent_id: string
  project_name: string
  status: 'stopped' | 'running' | 'paused' | 'crashed'
  mode: 'separate' | 'collaborative' | 'worktree'
  pid: number | null
  started_at: string | null
  current_feature_id: number | null
  worktree_path: string | null
}

export interface SpawnAgentRequest {
  mode?: 'separate' | 'collaborative' | 'worktree'
  worktree_path?: string
}

export interface StartAgentRequest {
  yolo_mode?: boolean
  model?: string
}

export const multiAgentAPI = {
  list: (projectName: string): Promise<{ agents: MultiAgentInfo[] }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents`),

  spawn: (projectName: string, options?: SpawnAgentRequest): Promise<MultiAgentInfo> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  getStatus: (projectName: string, agentId: string): Promise<MultiAgentInfo> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/${agentId}/status`),

  start: (projectName: string, agentId: string, options?: StartAgentRequest): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/${agentId}/start`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  stop: (projectName: string, agentId: string): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/${agentId}/stop`, {
      method: 'POST',
    }),

  pause: (projectName: string, agentId: string): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/${agentId}/pause`, {
      method: 'POST',
    }),

  resume: (projectName: string, agentId: string): Promise<AgentActionResponse> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/${agentId}/resume`, {
      method: 'POST',
    }),

  remove: (projectName: string, agentId: string): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/${agentId}`, {
      method: 'DELETE',
    }),

  stopAll: (projectName: string): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/stop-all`, {
      method: 'POST',
    }),

  getLockedFeatures: (projectName: string): Promise<{ locked_features: Record<number, string> }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/agents/locked-features`),
}

// ============================================================================
// Assets API
// ============================================================================

export interface AssetInfo {
  filename: string
  path: string
  size: number
  mime_type: string | null
  modified_at: string | null
}

export interface AssetUploadResponse {
  success: boolean
  filename: string
  original_filename: string
  path: string
  size: number
  mime_type: string | null
  spec_reference: string
}

export const assetsAPI = {
  list: (projectName: string): Promise<{ assets: AssetInfo[]; count: number; total_size: number }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/assets`),

  get: (projectName: string, filename: string): Promise<AssetInfo & { spec_reference: string; relative_path: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/assets/${encodeURIComponent(filename)}`),

  upload: async (projectName: string, file: File, overwrite: boolean = false): Promise<AssetUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const token = getAuthToken()
    const headers: Record<string, string> = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(
      `/api/projects/${encodeURIComponent(projectName)}/assets?overwrite=${overwrite}`,
      {
        method: 'POST',
        headers,
        body: formData,
      }
    )

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  },

  delete: (projectName: string, filename: string): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/assets/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    }),

  getStats: (projectName: string): Promise<{ total_count: number; total_size: number; by_type: Record<string, { count: number; size: number }> }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/assets-stats`),
}

// ============================================================================
// Project Config API
// ============================================================================

export interface ProjectConfig {
  project_name: string
  max_parallel_agents: number
  default_mode: 'separate' | 'collaborative' | 'worktree'
  use_worktrees: boolean
  auto_stop_on_completion: boolean
  subagent_config: SubagentConfig | null
  updated_at: string | null
}

export interface SubagentConfig {
  subagents: Subagent[]
}

export interface Subagent {
  name: string
  description: string
  prompt: string
  trigger: 'manual' | 'after_feature_complete' | 'on_error'
  tools: string[]
}

export interface ProjectConfigUpdate {
  max_parallel_agents?: number
  default_mode?: 'separate' | 'collaborative' | 'worktree'
  use_worktrees?: boolean
  auto_stop_on_completion?: boolean
}

export const configAPI = {
  get: (projectName: string): Promise<ProjectConfig> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/config`),

  update: (projectName: string, config: ProjectConfigUpdate): Promise<ProjectConfig> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/config`, {
      method: 'PUT',
      body: JSON.stringify(config),
    }),

  getSubagents: (projectName: string): Promise<SubagentConfig> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/config/subagents`),

  updateSubagents: (projectName: string, config: SubagentConfig): Promise<SubagentConfig> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/config/subagents`, {
      method: 'PUT',
      body: JSON.stringify(config),
    }),

  triggerSubagent: (projectName: string, subagentName: string): Promise<{ success: boolean; message: string; subagent: Subagent }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/config/subagents/${encodeURIComponent(subagentName)}/trigger`, {
      method: 'POST',
    }),

  deleteSubagent: (projectName: string, subagentName: string): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/config/subagents/${encodeURIComponent(subagentName)}`, {
      method: 'DELETE',
    }),
}

// ============================================================================
// Worktrees API
// ============================================================================

export interface WorktreeInfo {
  agent_id: string
  path: string
  branch: string | null
  has_changes: boolean
}

export const worktreesAPI = {
  list: (projectName: string): Promise<{ worktrees: WorktreeInfo[] }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees`),

  create: (projectName: string, agentId: string, branch?: string): Promise<{ success: boolean; agent_id: string; path: string; branch: string; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees`, {
      method: 'POST',
      body: JSON.stringify({ agent_id: agentId, branch }),
    }),

  getStatus: (projectName: string, agentId: string): Promise<WorktreeInfo> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees/${agentId}`),

  merge: (projectName: string, agentId: string, targetBranch: string = 'main'): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees/${agentId}/merge`, {
      method: 'POST',
      body: JSON.stringify({ target_branch: targetBranch }),
    }),

  delete: (projectName: string, agentId: string): Promise<{ success: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees/${agentId}`, {
      method: 'DELETE',
    }),

  sync: (projectName: string, targetBranch: string = 'main'): Promise<{ results: Record<string, { success: boolean; message: string }> }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees/sync?target_branch=${targetBranch}`, {
      method: 'POST',
    }),

  isGitRepo: (projectName: string): Promise<{ is_git_repo: boolean }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees/is-git-repo`),

  initRepo: (projectName: string): Promise<{ success: boolean; is_git_repo: boolean; message: string }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/worktrees/init`, {
      method: 'POST',
    }),
}

// ============================================================================
// Questions API (Agent Clarifying Questions)
// ============================================================================

export interface AgentQuestion {
  id: string
  question: string
  context?: string | null
  options?: string[] | null
  timestamp: string
  answered: boolean
  answer?: string | null
  answered_at?: string | null
}

export const questionsAPI = {
  list: (projectName: string): Promise<{ questions: AgentQuestion[] }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/questions`),

  getPending: (projectName: string): Promise<{ question: AgentQuestion | null }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/questions/pending`),

  create: (projectName: string, question: string, context?: string, options?: string[]): Promise<{ question: AgentQuestion }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/questions`, {
      method: 'POST',
      body: JSON.stringify({ question, context, options }),
    }),

  answer: (projectName: string, questionId: string, answer: string): Promise<{ success: boolean }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/questions/${encodeURIComponent(questionId)}/answer`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    }),

  clear: (projectName: string): Promise<{ success: boolean }> =>
    fetchJSON(`/projects/${encodeURIComponent(projectName)}/questions`, {
      method: 'DELETE',
    }),
}

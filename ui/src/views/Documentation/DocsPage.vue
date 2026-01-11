<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Documentation'" />

    <div class="space-y-6">
      <!-- Header -->
      <div class="rounded-2xl border border-brand-200 bg-gradient-to-r from-brand-50 to-brand-100/50 p-6 dark:border-brand-800 dark:from-brand-900/20 dark:to-brand-900/10">
        <div class="flex items-center gap-4">
          <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-500 text-white">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-800 dark:text-white/90">
              Nexus Documentation
            </h1>
            <p class="text-gray-600 dark:text-gray-400">
              Complete guide to the Autonomous Coding Platform
            </p>
          </div>
        </div>
      </div>

      <!-- Quick Navigation -->
      <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
        <button
          v-for="section in quickNavSections"
          :key="section.id"
          @click="scrollToSection(section.id)"
          class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-3 text-left transition hover:border-brand-300 hover:shadow-md dark:border-gray-800 dark:bg-white/[0.03] dark:hover:border-brand-800"
        >
          <div :class="['flex h-9 w-9 items-center justify-center rounded-lg', section.bgClass]">
            <component :is="section.icon" class="w-4 h-4" :class="section.iconClass" />
          </div>
          <div>
            <p class="text-sm font-medium text-gray-800 dark:text-white/90">{{ section.title }}</p>
          </div>
        </button>
      </div>

      <!-- How Nexus Works -->
      <section id="how-it-works" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          How Nexus Works
        </h2>

        <div class="space-y-4">
          <p class="text-gray-600 dark:text-gray-400">
            Nexus uses a <strong>two-agent pattern</strong> to build complete applications autonomously. The system reads your specification and implements features one by one until the entire application is complete.
          </p>

          <!-- Architecture Diagram -->
          <div class="rounded-lg bg-gray-900 p-4 font-mono text-xs text-green-400 overflow-x-auto">
            <pre>
┌─────────────────────────────────────────────────────────────────────┐
│                        YOUR APP SPECIFICATION                        │
│                    (What you want to build)                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      INITIALIZER AGENT (Session 1)                   │
│  • Reads your app_spec.txt                                          │
│  • Creates feature test cases in features.db                        │
│  • Sets up project structure                                        │
│  • Initializes git repository                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CODING AGENT (Sessions 2+)                        │
│  • Picks next pending feature                                       │
│  • Writes code to implement feature                                 │
│  • Runs tests (Playwright browser tests in Standard mode)           │
│  • Marks feature as passing                                         │
│  • Commits changes to git                                           │
│  • Repeats until all features complete                              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      COMPLETED APPLICATION                           │
│                    (Ready to run and deploy)                         │
└─────────────────────────────────────────────────────────────────────┘
            </pre>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 mt-4">
            <div class="rounded-lg bg-brand-50 p-4 dark:bg-brand-900/20">
              <h3 class="font-semibold text-brand-700 dark:text-brand-400 mb-2">Initializer Agent</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Runs <strong>once</strong> when you first start a project. Reads your specification and creates detailed feature test cases. Each feature includes:
              </p>
              <ul class="text-sm text-gray-600 dark:text-gray-400 mt-2 space-y-1 ml-4 list-disc">
                <li>Category (UI, API, Database, etc.)</li>
                <li>Feature name and description</li>
                <li>Step-by-step verification instructions</li>
                <li>Priority for implementation order</li>
              </ul>
            </div>

            <div class="rounded-lg bg-success-50 p-4 dark:bg-success-900/20">
              <h3 class="font-semibold text-success-700 dark:text-success-400 mb-2">Coding Agent</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Runs <strong>repeatedly</strong> until all features pass. Each session:
              </p>
              <ul class="text-sm text-gray-600 dark:text-gray-400 mt-2 space-y-1 ml-4 list-disc">
                <li>Gets next pending feature from queue</li>
                <li>Implements the feature in code</li>
                <li>Runs verification tests</li>
                <li>Performs regression testing on completed features</li>
                <li>Auto-continues to next feature (3s delay)</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Getting Started -->
      <section id="getting-started" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Getting Started
        </h2>

        <div class="space-y-4">
          <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Step 1: Create a New Project</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Click <strong>"+ New Project"</strong> from the sidebar or dashboard.
            </p>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4 list-disc">
              <li>Enter a unique project name (letters, numbers, hyphens, underscores)</li>
              <li>Select a folder location for your project files</li>
              <li>Choose how to create your spec: <strong>Claude AI</strong> (recommended) or <strong>Manual</strong></li>
            </ul>
          </div>

          <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Step 2: Write Your App Specification</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              The app spec describes what you want to build. This is the most important step!
            </p>
            <div class="bg-white dark:bg-gray-900 rounded p-3 mt-2">
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Example specification structure:</p>
              <pre class="text-xs text-gray-700 dark:text-gray-300 overflow-x-auto">&lt;app&gt;
  &lt;name&gt;Task Manager&lt;/name&gt;
  &lt;description&gt;A web app to manage tasks&lt;/description&gt;
  &lt;features&gt;
    &lt;feature&gt;User can create new tasks&lt;/feature&gt;
    &lt;feature&gt;User can mark tasks complete&lt;/feature&gt;
    &lt;feature&gt;Tasks persist in database&lt;/feature&gt;
  &lt;/features&gt;
  &lt;tech_stack&gt;
    &lt;frontend&gt;Vue 3, TypeScript, Tailwind&lt;/frontend&gt;
    &lt;backend&gt;FastAPI, SQLite&lt;/backend&gt;
  &lt;/tech_stack&gt;
&lt;/app&gt;</pre>
            </div>
          </div>

          <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Step 3: Start the Agent</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Click the <strong>green "Start Agent" button</strong> on the project detail page.
            </p>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4 list-disc">
              <li><strong>First run:</strong> Initializer agent creates features (takes several minutes)</li>
              <li><strong>Subsequent runs:</strong> Coding agent implements features one by one</li>
              <li>Watch real-time progress in the Agent Activity panel</li>
              <li>Features move from Pending → In Progress → Done on the Kanban board</li>
            </ul>
          </div>

          <div class="rounded-lg bg-warning-50 p-4 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800">
            <h3 class="font-medium text-warning-700 dark:text-warning-400 mb-2">⏱️ Time Expectations</h3>
            <ul class="text-sm text-warning-600 dark:text-warning-400/80 space-y-1 ml-4 list-disc">
              <li><strong>Initialization:</strong> 5-15 minutes to generate features</li>
              <li><strong>Per feature:</strong> 5-20 minutes depending on complexity</li>
              <li><strong>Full application:</strong> Several hours across multiple sessions</li>
              <li>The agent auto-continues - you can leave it running!</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Agent Modes -->
      <section id="agent-modes" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-warning-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Agent Modes
        </h2>

        <div class="space-y-4">
          <div class="flex gap-4 rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-brand-100 dark:bg-brand-500/20">
              <svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-800 dark:text-white/90">Standard Mode (Recommended)</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Full testing and verification. Each feature is tested in a real browser using Playwright automation before being marked as complete.
              </p>
              <div class="mt-2 flex flex-wrap gap-2">
                <span class="inline-flex items-center rounded-full bg-brand-100 px-2 py-1 text-xs text-brand-700 dark:bg-brand-900/30 dark:text-brand-400">Browser Testing</span>
                <span class="inline-flex items-center rounded-full bg-brand-100 px-2 py-1 text-xs text-brand-700 dark:bg-brand-900/30 dark:text-brand-400">Regression Tests</span>
                <span class="inline-flex items-center rounded-full bg-brand-100 px-2 py-1 text-xs text-brand-700 dark:bg-brand-900/30 dark:text-brand-400">Production Quality</span>
              </div>
            </div>
          </div>

          <div class="flex gap-4 rounded-lg bg-warning-50 p-4 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-warning-100 dark:bg-warning-500/20">
              <svg class="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-warning-700 dark:text-warning-400">YOLO Mode (Fast Prototyping)</h3>
              <p class="text-sm text-warning-600 dark:text-warning-400/80 mt-1">
                Skips browser testing for rapid iteration. Features are marked complete after the code compiles and passes lint checks. Toggle the ⚡ lightning bolt icon to enable.
              </p>
              <div class="mt-2 flex flex-wrap gap-2">
                <span class="inline-flex items-center rounded-full bg-warning-100 px-2 py-1 text-xs text-warning-700 dark:bg-warning-900/30 dark:text-warning-400">3-5x Faster</span>
                <span class="inline-flex items-center rounded-full bg-warning-100 px-2 py-1 text-xs text-warning-700 dark:bg-warning-900/30 dark:text-warning-400">No Browser Tests</span>
                <span class="inline-flex items-center rounded-full bg-warning-100 px-2 py-1 text-xs text-warning-700 dark:bg-warning-900/30 dark:text-warning-400">Prototype Only</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Overview -->
      <section id="features" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          Platform Features
        </h2>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div class="rounded-lg border border-gray-100 p-4 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-2">
              <div class="h-8 w-8 rounded bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 class="font-medium text-gray-800 dark:text-white/90">Project Management</h3>
            </div>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Create unlimited projects</li>
              <li>• Pause, resume, restart projects</li>
              <li>• Track completion percentage</li>
              <li>• Archive finished projects</li>
            </ul>
          </div>

          <div class="rounded-lg border border-gray-100 p-4 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-2">
              <div class="h-8 w-8 rounded bg-success-100 dark:bg-success-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h3 class="font-medium text-gray-800 dark:text-white/90">Feature Tracking</h3>
            </div>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Kanban board visualization</li>
              <li>• Add features on-the-fly</li>
              <li>• Edit feature descriptions</li>
              <li>• Skip or requeue features</li>
            </ul>
          </div>

          <div class="rounded-lg border border-gray-100 p-4 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-2">
              <div class="h-8 w-8 rounded bg-warning-100 dark:bg-warning-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 class="font-medium text-gray-800 dark:text-white/90">Multi-Agent Support</h3>
            </div>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Run parallel agents</li>
              <li>• Work on different features</li>
              <li>• Git worktree isolation</li>
              <li>• Auto-merge on completion</li>
            </ul>
          </div>

          <div class="rounded-lg border border-gray-100 p-4 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-2">
              <div class="h-8 w-8 rounded bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 class="font-medium text-gray-800 dark:text-white/90">Asset Management</h3>
            </div>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Upload images & files</li>
              <li>• Reference in app specs</li>
              <li>• Automatic organization</li>
              <li>• 10MB file size limit</li>
            </ul>
          </div>

          <div class="rounded-lg border border-gray-100 p-4 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-2">
              <div class="h-8 w-8 rounded bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="font-medium text-gray-800 dark:text-white/90">Agent Questions</h3>
            </div>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Agents ask for clarification</li>
              <li>• Answer via UI popup</li>
              <li>• Better decision making</li>
              <li>• Reduces wrong assumptions</li>
            </ul>
          </div>

          <div class="rounded-lg border border-gray-100 p-4 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-2">
              <div class="h-8 w-8 rounded bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 class="font-medium text-gray-800 dark:text-white/90">Code Validation</h3>
            </div>
            <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• OWASP Top 10 scanning</li>
              <li>• No mocks/stubs/TODOs</li>
              <li>• Security-first code</li>
              <li>• Auto-documentation</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Custom Subagents -->
      <section id="subagents" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Custom Subagents
        </h2>

        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Configure specialized agents that run automatically or on-demand. Find this in the <strong>"Custom Subagents"</strong> section on your project page.
        </p>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Test Runner</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Runs after each feature completes. Executes test suite and reports failures.
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-2">
              Trigger: <code class="bg-gray-200 dark:bg-gray-700 px-1 rounded">after_feature_complete</code>
            </p>
          </div>

          <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Code Reviewer</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Reviews code for best practices, security issues, and potential improvements.
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-2">
              Trigger: <code class="bg-gray-200 dark:bg-gray-700 px-1 rounded">manual</code>
            </p>
          </div>

          <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Error Handler</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Activates when the main agent encounters an error. Attempts to diagnose and fix.
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-2">
              Trigger: <code class="bg-gray-200 dark:bg-gray-700 px-1 rounded">on_error</code>
            </p>
          </div>
        </div>
      </section>

      <!-- Project Lifecycle -->
      <section id="lifecycle" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Project Lifecycle
        </h2>

        <div class="flex flex-wrap items-center gap-3 mb-6">
          <div class="flex items-center gap-2 rounded-full bg-success-100 px-4 py-2 dark:bg-success-900/20">
            <span class="h-2 w-2 rounded-full bg-success-500"></span>
            <span class="text-sm font-medium text-success-700 dark:text-success-400">Active</span>
          </div>
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <div class="flex items-center gap-2 rounded-full bg-warning-100 px-4 py-2 dark:bg-warning-900/20">
            <span class="h-2 w-2 rounded-full bg-warning-500"></span>
            <span class="text-sm font-medium text-warning-700 dark:text-warning-400">Paused</span>
          </div>
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <div class="flex items-center gap-2 rounded-full bg-brand-100 px-4 py-2 dark:bg-brand-900/20">
            <span class="h-2 w-2 rounded-full bg-brand-500"></span>
            <span class="text-sm font-medium text-brand-700 dark:text-brand-400">Finished</span>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-lg border border-gray-100 p-3 dark:border-gray-700">
            <p class="font-medium text-gray-800 dark:text-white/90">Pause</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Stop work temporarily, all progress saved</p>
          </div>
          <div class="rounded-lg border border-gray-100 p-3 dark:border-gray-700">
            <p class="font-medium text-gray-800 dark:text-white/90">Resume</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Continue from exactly where you stopped</p>
          </div>
          <div class="rounded-lg border border-gray-100 p-3 dark:border-gray-700">
            <p class="font-medium text-gray-800 dark:text-white/90">Reset</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Clear progress, keep feature definitions</p>
          </div>
          <div class="rounded-lg border border-gray-100 p-3 dark:border-gray-700">
            <p class="font-medium text-gray-800 dark:text-white/90">Restart</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Delete everything, start completely fresh</p>
          </div>
        </div>
      </section>

      <!-- Configuration -->
      <section id="configuration" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Configuration
        </h2>

        <div class="space-y-4">
          <div>
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-3">Environment Variables</h3>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-gray-200 dark:border-gray-700">
                    <th class="text-left py-2 pr-4 font-medium text-gray-700 dark:text-gray-300">Variable</th>
                    <th class="text-left py-2 pr-4 font-medium text-gray-700 dark:text-gray-300">Default</th>
                    <th class="text-left py-2 font-medium text-gray-700 dark:text-gray-300">Description</th>
                  </tr>
                </thead>
                <tbody class="text-gray-600 dark:text-gray-400">
                  <tr class="border-b border-gray-100 dark:border-gray-800">
                    <td class="py-2 pr-4 font-mono text-xs">NEXUS_AUTO_CONTINUE_DELAY</td>
                    <td class="py-2 pr-4">3</td>
                    <td class="py-2">Seconds between agent sessions</td>
                  </tr>
                  <tr class="border-b border-gray-100 dark:border-gray-800">
                    <td class="py-2 pr-4 font-mono text-xs">NEXUS_MAX_FEATURE_ATTEMPTS</td>
                    <td class="py-2 pr-4">3</td>
                    <td class="py-2">Max retries per feature before marking stuck</td>
                  </tr>
                  <tr class="border-b border-gray-100 dark:border-gray-800">
                    <td class="py-2 pr-4 font-mono text-xs">NEXUS_MAX_COST_USD</td>
                    <td class="py-2 pr-4">0</td>
                    <td class="py-2">Cost limit in USD (0 = unlimited)</td>
                  </tr>
                  <tr>
                    <td class="py-2 pr-4 font-mono text-xs">NEXUS_MAX_TOKENS</td>
                    <td class="py-2 pr-4">0</td>
                    <td class="py-2">Token limit (0 = unlimited)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-3">Project Config Options</h3>
            <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
                <p class="font-medium text-gray-800 dark:text-white/90 text-sm">Max Parallel Agents</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">1-10 agents working simultaneously</p>
              </div>
              <div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
                <p class="font-medium text-gray-800 dark:text-white/90 text-sm">Use Git Worktrees</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">Isolate parallel agent work in branches</p>
              </div>
              <div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
                <p class="font-medium text-gray-800 dark:text-white/90 text-sm">Auto-Stop on Completion</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">Stop agents when all features pass</p>
              </div>
              <div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
                <p class="font-medium text-gray-800 dark:text-white/90 text-sm">Default Mode</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">Standard, YOLO, or Worktree mode</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Troubleshooting -->
      <section id="troubleshooting" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Troubleshooting
        </h2>

        <div class="space-y-4">
          <div class="rounded-lg border-l-4 border-red-500 bg-red-50 p-4 dark:bg-red-900/10">
            <h3 class="font-medium text-red-700 dark:text-red-400">"Agent appears stuck on first run"</h3>
            <p class="text-sm text-red-600 dark:text-red-400/80 mt-1">
              This is normal! The initializer agent is generating detailed feature test cases. This can take 5-15 minutes. Watch the Agent Activity panel for progress.
            </p>
          </div>

          <div class="rounded-lg border-l-4 border-warning-500 bg-warning-50 p-4 dark:bg-warning-900/10">
            <h3 class="font-medium text-warning-700 dark:text-warning-400">"Command blocked by security hook"</h3>
            <p class="text-sm text-warning-600 dark:text-warning-400/80 mt-1">
              The agent tried to run a command not in the allowlist. This is the security system working correctly. If needed, add the command to <code class="bg-warning-100 dark:bg-warning-900/30 px-1 rounded">security.py</code>.
            </p>
          </div>

          <div class="rounded-lg border-l-4 border-brand-500 bg-brand-50 p-4 dark:bg-brand-900/10">
            <h3 class="font-medium text-brand-700 dark:text-brand-400">"Feature keeps failing after multiple attempts"</h3>
            <p class="text-sm text-brand-600 dark:text-brand-400/80 mt-1">
              Try: 1) Check the feature description for clarity, 2) Use "Skip" to move to next feature, 3) Edit the feature with more specific instructions, 4) Check Agent Activity for error details.
            </p>
          </div>

          <div class="rounded-lg border-l-4 border-gray-500 bg-gray-50 p-4 dark:bg-gray-800/50">
            <h3 class="font-medium text-gray-700 dark:text-gray-300">"WebSocket disconnected"</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              The UI will automatically reconnect. If issues persist, refresh the page. The agent continues running in the background regardless of UI connection.
            </p>
          </div>
        </div>
      </section>

      <!-- Tips & Best Practices -->
      <section id="tips" class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Tips & Best Practices
        </h2>

        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <div class="flex gap-3 rounded-lg bg-brand-50 p-3 dark:bg-brand-900/10">
            <span class="text-brand-500 font-bold">1</span>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>Write detailed specs.</strong> The more context you provide, the better the agent implements features.
            </p>
          </div>
          <div class="flex gap-3 rounded-lg bg-brand-50 p-3 dark:bg-brand-900/10">
            <span class="text-brand-500 font-bold">2</span>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>Start with YOLO mode.</strong> Use rapid mode for prototypes, switch to standard for final polish.
            </p>
          </div>
          <div class="flex gap-3 rounded-lg bg-brand-50 p-3 dark:bg-brand-900/10">
            <span class="text-brand-500 font-bold">3</span>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>Review logs regularly.</strong> The Activity panel shows real-time agent decisions and actions.
            </p>
          </div>
          <div class="flex gap-3 rounded-lg bg-brand-50 p-3 dark:bg-brand-900/10">
            <span class="text-brand-500 font-bold">4</span>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>Add features incrementally.</strong> Use "+ Add Feature" to expand scope while agent runs.
            </p>
          </div>
          <div class="flex gap-3 rounded-lg bg-brand-50 p-3 dark:bg-brand-900/10">
            <span class="text-brand-500 font-bold">5</span>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>Use assets for UI mockups.</strong> Upload images to guide visual implementation.
            </p>
          </div>
          <div class="flex gap-3 rounded-lg bg-brand-50 p-3 dark:bg-brand-900/10">
            <span class="text-brand-500 font-bold">6</span>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>Monitor usage.</strong> Check Analytics to track token consumption and costs.
            </p>
          </div>
        </div>
      </section>

      <!-- Keyboard Shortcuts -->
      <section class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 class="flex items-center gap-2 text-xl font-semibold text-gray-800 dark:text-white/90 mb-4">
          <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          Keyboard Shortcuts
        </h2>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Global</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600 dark:text-gray-400">Command Palette</span>
                <span class="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs dark:bg-gray-800">Ctrl+K / ⌘K</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600 dark:text-gray-400">Toggle Theme</span>
                <span class="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs dark:bg-gray-800">Header icon</span>
              </div>
            </div>
          </div>
          <div>
            <h3 class="font-medium text-gray-800 dark:text-white/90 mb-2">Project Page</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600 dark:text-gray-400">Start/Stop Agent</span>
                <span class="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs dark:bg-gray-800">Play/Stop btn</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600 dark:text-gray-400">Toggle YOLO Mode</span>
                <span class="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs dark:bg-gray-800">⚡ Lightning</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Version Info -->
      <div class="text-center text-sm text-gray-500 dark:text-gray-400">
        <p>Nexus - Autonomous Coding Platform</p>
        <p class="text-xs mt-1">Powered by Claude AI | Inspired by <a href="https://github.com/leonvanzyl/autocoder" class="text-brand-500 hover:underline" target="_blank">leonvanzyl/autocoder</a></p>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { markRaw } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'

// Simple inline SVG components for icons
const RocketIcon = markRaw({
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>`
})

const ComputerIcon = markRaw({
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>`
})

const CheckBadgeIcon = markRaw({
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" /></svg>`
})

const LightBulbIcon = markRaw({
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>`
})

const CogIcon = markRaw({
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`
})

const WarningIcon = markRaw({
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>`
})

const quickNavSections = [
  {
    id: 'how-it-works',
    title: 'How It Works',
    icon: ComputerIcon,
    bgClass: 'bg-brand-100 dark:bg-brand-500/20',
    iconClass: 'text-brand-600',
  },
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: RocketIcon,
    bgClass: 'bg-success-100 dark:bg-success-500/20',
    iconClass: 'text-success-600',
  },
  {
    id: 'features',
    title: 'Features',
    icon: CheckBadgeIcon,
    bgClass: 'bg-purple-100 dark:bg-purple-500/20',
    iconClass: 'text-purple-600',
  },
  {
    id: 'configuration',
    title: 'Configuration',
    icon: CogIcon,
    bgClass: 'bg-gray-100 dark:bg-gray-500/20',
    iconClass: 'text-gray-600',
  },
  {
    id: 'troubleshooting',
    title: 'Troubleshooting',
    icon: WarningIcon,
    bgClass: 'bg-red-100 dark:bg-red-500/20',
    iconClass: 'text-red-600',
  },
  {
    id: 'tips',
    title: 'Tips & Tricks',
    icon: LightBulbIcon,
    bgClass: 'bg-warning-100 dark:bg-warning-500/20',
    iconClass: 'text-warning-600',
  },
]

function scrollToSection(id: string) {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

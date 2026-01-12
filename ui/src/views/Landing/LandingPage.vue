<template>
  <div class="min-h-screen bg-white dark:bg-gray-900">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <svg
              width="36"
              height="36"
              viewBox="0 0 64 64"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              class="text-brand-500"
            >
              <path
                d="M32 4L4 18V46L32 60L60 46V18L32 4Z"
                stroke="currentColor"
                stroke-width="3"
                fill="none"
              />
              <path
                d="M32 4V32M32 32L4 18M32 32L60 18M32 32V60"
                stroke="currentColor"
                stroke-width="3"
              />
              <circle cx="32" cy="32" r="8" fill="currentColor" />
            </svg>
            <span class="text-xl font-bold text-gray-900 dark:text-white">Nexus</span>
          </div>

          <!-- Nav Links -->
          <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition">Features</a>
            <a href="#how-it-works" class="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition">How it Works</a>
            <a
              href="https://github.com/undilutedtech/Nexus-Autonomous-Claude-Code"
              target="_blank"
              class="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition flex items-center gap-1.5"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              GitHub
            </a>
          </div>

          <!-- CTA Buttons -->
          <div class="flex items-center gap-3">
            <template v-if="isAuthenticated">
              <router-link
                to="/dashboard"
                class="px-5 py-2.5 text-sm font-semibold text-white bg-brand-500 hover:bg-brand-600 rounded-lg transition shadow-lg shadow-brand-500/25"
              >
                Go to Dashboard
              </router-link>
            </template>
            <template v-else>
              <router-link
                to="/signin"
                class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition"
              >
                Sign In
              </router-link>
              <router-link
                to="/signup"
                class="px-5 py-2.5 text-sm font-semibold text-white bg-brand-500 hover:bg-brand-600 rounded-lg transition shadow-lg shadow-brand-500/25"
              >
                Get Started
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative pt-32 pb-20 lg:pt-44 lg:pb-32 overflow-hidden">
      <!-- Background Elements -->
      <div class="absolute inset-0 -z-10">
        <div class="absolute top-0 right-0 w-[600px] h-[600px] bg-brand-500/5 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-3xl"></div>
      </div>
      <div class="absolute right-0 top-20 -z-1 w-full max-w-[250px] xl:max-w-[450px] opacity-20 dark:opacity-10">
        <img src="/images/shape/grid-01.svg" alt="grid" />
      </div>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-4xl mx-auto">
          <!-- Badge -->
          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-50 dark:bg-brand-500/10 border border-brand-200 dark:border-brand-500/20 mb-8">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
            </span>
            <span class="text-sm font-medium text-brand-600 dark:text-brand-400">Powered by Claude AI</span>
          </div>

          <!-- Heading -->
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
            Build Complete Apps with
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-brand-500 via-purple-500 to-brand-600">
              Autonomous AI Agents
            </span>
          </h1>

          <!-- Subheading -->
          <p class="text-lg lg:text-xl text-gray-600 dark:text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Transform your app specifications into fully functional applications.
            Watch as intelligent agents implement, test, and deliver features automatically.
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <router-link
              :to="isAuthenticated ? '/projects' : '/signup'"
              class="w-full sm:w-auto px-8 py-4 text-base font-semibold text-white bg-brand-500 hover:bg-brand-600 rounded-xl transition-all shadow-xl shadow-brand-500/25 hover:shadow-brand-500/40 hover:-translate-y-0.5 flex items-center justify-center gap-2"
            >
              {{ isAuthenticated ? 'View Projects' : 'Start Building Free' }}
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </router-link>
            <a
              href="https://github.com/undilutedtech/Nexus-Autonomous-Claude-Code"
              target="_blank"
              class="w-full sm:w-auto px-8 py-4 text-base font-semibold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              View on GitHub
            </a>
          </div>

          <!-- Hero Image / Dashboard Preview -->
          <div class="relative mx-auto max-w-5xl perspective-1000">
            <div
              class="relative transform-gpu transition-all duration-500 ease-out hover:scale-[1.02]"
              :style="{ transform: `rotateX(${tiltX}deg) rotateY(${tiltY}deg)` }"
              @mousemove="handleMouseMove"
              @mouseleave="resetTilt"
            >
              <!-- Glow -->
              <div class="absolute -inset-4 bg-gradient-to-r from-brand-500/20 via-purple-500/20 to-brand-500/20 rounded-3xl blur-2xl opacity-60"></div>

              <!-- Browser Frame -->
              <div class="relative rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 shadow-2xl bg-white dark:bg-gray-800">
                <!-- Browser Chrome -->
                <div class="flex items-center gap-2 px-4 py-3 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                  <div class="flex gap-1.5">
                    <div class="w-3 h-3 rounded-full bg-red-400"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div class="w-3 h-3 rounded-full bg-green-400"></div>
                  </div>
                  <div class="flex-1 mx-4">
                    <div class="max-w-sm mx-auto bg-gray-200 dark:bg-gray-700 rounded-lg px-4 py-1.5 text-xs text-gray-500 dark:text-gray-400 text-center font-mono">
                      localhost:5173/dashboard
                    </div>
                  </div>
                </div>

                <!-- Dashboard Mockup -->
                <div class="aspect-[16/10] bg-gray-50 dark:bg-gray-900 p-4 lg:p-6">
                  <div class="h-full flex gap-4">
                    <!-- Sidebar Mock -->
                    <div class="hidden sm:flex w-16 lg:w-20 bg-white dark:bg-gray-800 rounded-xl flex-col items-center py-4 gap-3 border border-gray-200 dark:border-gray-700">
                      <div class="w-8 h-8 lg:w-10 lg:h-10 rounded-xl bg-brand-500 flex items-center justify-center">
                        <svg class="w-4 h-4 lg:w-5 lg:h-5 text-white" viewBox="0 0 64 64" fill="none">
                          <path d="M32 4L4 18V46L32 60L60 46V18L32 4Z" stroke="currentColor" stroke-width="4" fill="none"/>
                          <circle cx="32" cy="32" r="6" fill="currentColor"/>
                        </svg>
                      </div>
                      <div class="w-8 h-8 lg:w-10 lg:h-10 rounded-lg bg-gray-100 dark:bg-gray-700"></div>
                      <div class="w-8 h-8 lg:w-10 lg:h-10 rounded-lg bg-gray-100 dark:bg-gray-700"></div>
                      <div class="w-8 h-8 lg:w-10 lg:h-10 rounded-lg bg-gray-100 dark:bg-gray-700"></div>
                    </div>

                    <!-- Main Content -->
                    <div class="flex-1 flex flex-col gap-4">
                      <!-- Stats Row -->
                      <div class="grid grid-cols-3 gap-3 lg:gap-4">
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-3 lg:p-4 border border-gray-200 dark:border-gray-700">
                          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Total Features</div>
                          <div class="text-lg lg:text-2xl font-bold text-gray-900 dark:text-white">24</div>
                        </div>
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-3 lg:p-4 border border-gray-200 dark:border-gray-700">
                          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Completed</div>
                          <div class="text-lg lg:text-2xl font-bold text-success-500">18</div>
                        </div>
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-3 lg:p-4 border border-gray-200 dark:border-gray-700">
                          <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Progress</div>
                          <div class="text-lg lg:text-2xl font-bold text-brand-500">75%</div>
                        </div>
                      </div>

                      <!-- Kanban Preview -->
                      <div class="flex-1 grid grid-cols-3 gap-3 lg:gap-4">
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700">
                          <div class="flex items-center gap-2 mb-3">
                            <div class="w-2 h-2 rounded-full bg-yellow-400"></div>
                            <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Pending</span>
                          </div>
                          <div class="space-y-2">
                            <div class="h-10 lg:h-14 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
                            <div class="h-10 lg:h-14 bg-gray-100 dark:bg-gray-700 rounded-lg"></div>
                          </div>
                        </div>
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700">
                          <div class="flex items-center gap-2 mb-3">
                            <div class="w-2 h-2 rounded-full bg-cyan-400"></div>
                            <span class="text-xs font-medium text-gray-600 dark:text-gray-400">In Progress</span>
                          </div>
                          <div class="space-y-2">
                            <div class="h-10 lg:h-14 bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/20 rounded-lg flex items-center px-2">
                              <div class="w-full bg-cyan-200 dark:bg-cyan-500/30 h-1 rounded-full overflow-hidden">
                                <div class="w-2/3 h-full bg-cyan-500 rounded-full animate-pulse"></div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div class="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700">
                          <div class="flex items-center gap-2 mb-3">
                            <div class="w-2 h-2 rounded-full bg-success-500"></div>
                            <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Done</span>
                          </div>
                          <div class="space-y-2">
                            <div class="h-10 lg:h-14 bg-success-50 dark:bg-success-500/10 border border-success-200 dark:border-success-500/20 rounded-lg"></div>
                            <div class="h-10 lg:h-14 bg-success-50 dark:bg-success-500/10 border border-success-200 dark:border-success-500/20 rounded-lg"></div>
                            <div class="h-10 lg:h-14 bg-success-50 dark:bg-success-500/10 border border-success-200 dark:border-success-500/20 rounded-lg"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 lg:py-32 bg-gray-50 dark:bg-gray-800/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Everything You Need
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Powerful features designed for autonomous application development
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="group p-6 lg:p-8 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-brand-300 dark:hover:border-brand-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-brand-500/5"
          >
            <div
              class="w-14 h-14 rounded-2xl flex items-center justify-center mb-5 transition-transform group-hover:scale-110"
              :class="feature.bgClass"
            >
              <component :is="feature.icon" :class="feature.iconClass" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ feature.title }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-20 lg:py-32">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            How It Works
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Three simple steps to autonomous app development
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8 lg:gap-12">
          <div
            v-for="(step, index) in steps"
            :key="step.title"
            class="relative text-center"
          >
            <!-- Connector -->
            <div
              v-if="index < steps.length - 1"
              class="hidden md:block absolute top-10 left-1/2 w-full h-0.5 bg-gradient-to-r from-brand-500 to-transparent"
            ></div>

            <div class="relative inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-brand-500 text-white mb-6 shadow-lg shadow-brand-500/30">
              <span class="text-3xl font-bold">{{ index + 1 }}</span>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">
              {{ step.title }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
              {{ step.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 lg:py-32 bg-brand-950 dark:bg-gray-800 relative overflow-hidden">
      <!-- Background Pattern -->
      <div class="absolute right-0 top-0 -z-1 w-full max-w-[450px] opacity-10">
        <img src="/images/shape/grid-01.svg" alt="grid" />
      </div>
      <div class="absolute bottom-0 left-0 -z-1 w-full max-w-[450px] rotate-180 opacity-10">
        <img src="/images/shape/grid-01.svg" alt="grid" />
      </div>

      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <div class="mb-8">
          <svg
            width="64"
            height="64"
            viewBox="0 0 64 64"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            class="mx-auto text-white mb-6"
          >
            <path
              d="M32 4L4 18V46L32 60L60 46V18L32 4Z"
              stroke="currentColor"
              stroke-width="3"
              fill="none"
            />
            <path
              d="M32 4V32M32 32L4 18M32 32L60 18M32 32V60"
              stroke="currentColor"
              stroke-width="3"
            />
            <circle cx="32" cy="32" r="8" fill="currentColor" />
          </svg>
        </div>
        <h2 class="text-3xl lg:text-4xl font-bold text-white mb-4">
          Ready to Build Something Amazing?
        </h2>
        <p class="text-lg text-gray-400 mb-10 max-w-xl mx-auto">
          Join developers using Nexus to build applications faster than ever before.
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <template v-if="isAuthenticated">
            <router-link
              to="/projects/new"
              class="w-full sm:w-auto px-8 py-4 text-base font-semibold text-brand-950 bg-white hover:bg-gray-100 rounded-xl transition-all shadow-xl flex items-center justify-center gap-2"
            >
              Create New Project
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </router-link>
            <router-link
              to="/dashboard"
              class="w-full sm:w-auto px-8 py-4 text-base font-semibold text-white border border-white/20 hover:bg-white/10 rounded-xl transition-all flex items-center justify-center"
            >
              Go to Dashboard
            </router-link>
          </template>
          <template v-else>
            <router-link
              to="/signup"
              class="w-full sm:w-auto px-8 py-4 text-base font-semibold text-brand-950 bg-white hover:bg-gray-100 rounded-xl transition-all shadow-xl flex items-center justify-center gap-2"
            >
              Create Free Account
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </router-link>
            <router-link
              to="/signin"
              class="w-full sm:w-auto px-8 py-4 text-base font-semibold text-white border border-white/20 hover:bg-white/10 rounded-xl transition-all flex items-center justify-center"
            >
              Sign In
            </router-link>
          </template>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-8 border-t border-gray-200 dark:border-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <svg
              width="28"
              height="28"
              viewBox="0 0 64 64"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              class="text-brand-500"
            >
              <path
                d="M32 4L4 18V46L32 60L60 46V18L32 4Z"
                stroke="currentColor"
                stroke-width="3"
                fill="none"
              />
              <path
                d="M32 4V32M32 32L4 18M32 32L60 18M32 32V60"
                stroke="currentColor"
                stroke-width="3"
              />
              <circle cx="32" cy="32" r="8" fill="currentColor" />
            </svg>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Nexus - Autonomous Coding Platform
            </span>
          </div>
          <div class="flex items-center gap-6">
            <a
              href="https://github.com/undilutedtech/Nexus-Autonomous-Claude-Code"
              target="_blank"
              class="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition flex items-center gap-1.5"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              GitHub
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed } from 'vue'
import { getAuthToken } from '@/api/client'

// Check if user is authenticated
const isAuthenticated = computed(() => !!getAuthToken())

// 3D Tilt effect
const tiltX = ref(0)
const tiltY = ref(0)

function handleMouseMove(event: MouseEvent) {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  tiltY.value = ((x - centerX) / centerX) * 3
  tiltX.value = ((centerY - y) / centerY) * 3
}

function resetTilt() {
  tiltX.value = 0
  tiltY.value = 0
}

// Feature Icons
const BoltIcon = () => h('svg', { class: 'w-7 h-7', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' })
])

const CubeIcon = () => h('svg', { class: 'w-7 h-7', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' })
])

const CodeIcon = () => h('svg', { class: 'w-7 h-7', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' })
])

const ChartIcon = () => h('svg', { class: 'w-7 h-7', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
])

const ShieldIcon = () => h('svg', { class: 'w-7 h-7', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' })
])

const RefreshIcon = () => h('svg', { class: 'w-7 h-7', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' })
])

const features = [
  {
    icon: BoltIcon,
    title: 'AI-Powered Development',
    description: 'Intelligent agents understand your requirements and implement features automatically with minimal intervention.',
    bgClass: 'bg-brand-50 dark:bg-brand-500/10',
    iconClass: 'text-brand-500'
  },
  {
    icon: CubeIcon,
    title: 'Feature-Based Progress',
    description: 'Track development through a visual kanban board. Watch features move from pending to complete in real-time.',
    bgClass: 'bg-purple-50 dark:bg-purple-500/10',
    iconClass: 'text-purple-500'
  },
  {
    icon: CodeIcon,
    title: 'Two-Agent Pattern',
    description: 'Initializer agent creates features from specs, coding agent implements them. A proven autonomous pattern.',
    bgClass: 'bg-cyan-50 dark:bg-cyan-500/10',
    iconClass: 'text-cyan-500'
  },
  {
    icon: ChartIcon,
    title: 'Real-Time Analytics',
    description: 'Monitor token usage, costs, and development velocity across all your projects with detailed analytics.',
    bgClass: 'bg-success-50 dark:bg-success-500/10',
    iconClass: 'text-success-500'
  },
  {
    icon: ShieldIcon,
    title: 'Secure Execution',
    description: 'Sandboxed environments with command whitelisting ensure safe autonomous code execution.',
    bgClass: 'bg-orange-50 dark:bg-orange-500/10',
    iconClass: 'text-orange-500'
  },
  {
    icon: RefreshIcon,
    title: 'YOLO Mode',
    description: 'Rapid prototyping mode for quick iterations. Skip testing overhead when you need to move fast.',
    bgClass: 'bg-error-50 dark:bg-error-500/10',
    iconClass: 'text-error-500'
  }
]

const steps = [
  {
    title: 'Define Your Spec',
    description: 'Write a simple app specification describing what you want to build. The AI understands natural language requirements.'
  },
  {
    title: 'Agent Takes Over',
    description: 'The initializer creates features, then the coding agent implements them one by one, testing as it goes.'
  },
  {
    title: 'Ship Your App',
    description: 'Review completed features, make adjustments if needed, and deploy your fully functional application.'
  }
]
</script>

<style scoped>
.perspective-1000 {
  perspective: 1000px;
}

.transform-gpu {
  transform: translateZ(0);
  backface-visibility: hidden;
}
</style>

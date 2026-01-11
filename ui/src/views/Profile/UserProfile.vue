<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Profile'" />

    <div class="space-y-6">
      <!-- Profile Header -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <div class="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
          <div class="flex flex-col items-center w-full gap-6 xl:flex-row">
            <div
              class="w-20 h-20 overflow-hidden border border-gray-200 rounded-full dark:border-gray-800 bg-brand-100 dark:bg-brand-500/20 flex items-center justify-center"
            >
              <span class="text-2xl font-bold text-brand-600 dark:text-brand-400">
                {{ initials }}
              </span>
            </div>
            <div class="order-3 xl:order-2">
              <h4
                class="mb-2 text-lg font-semibold text-center text-gray-800 dark:text-white/90 xl:text-left"
              >
                {{ fullName || username }}
              </h4>
              <div
                class="flex flex-col items-center gap-1 text-center xl:flex-row xl:gap-3 xl:text-left"
              >
                <p class="text-sm text-gray-500 dark:text-gray-400">@{{ username }}</p>
                <div class="hidden h-3.5 w-px bg-gray-300 dark:bg-gray-700 xl:block"></div>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ email }}</p>
              </div>
            </div>
          </div>
          <button
            @click="showEditModal = true"
            class="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
              />
            </svg>
            Edit Profile
          </button>
        </div>
      </div>

      <!-- Account Information -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <h3 class="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">
          Account Information
        </h3>
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <p class="mb-1 text-sm text-gray-500 dark:text-gray-400">Full Name</p>
            <p class="font-medium text-gray-800 dark:text-white/90">
              {{ fullName || 'Not set' }}
            </p>
          </div>
          <div>
            <p class="mb-1 text-sm text-gray-500 dark:text-gray-400">Username</p>
            <p class="font-medium text-gray-800 dark:text-white/90">@{{ username }}</p>
          </div>
          <div>
            <p class="mb-1 text-sm text-gray-500 dark:text-gray-400">Email Address</p>
            <p class="font-medium text-gray-800 dark:text-white/90">{{ email }}</p>
          </div>
          <div>
            <p class="mb-1 text-sm text-gray-500 dark:text-gray-400">Bio</p>
            <p class="font-medium text-gray-800 dark:text-white/90">
              {{ user?.bio || 'No bio added' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Your Projects -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
            Your Projects
          </h3>
          <router-link
            to="/projects"
            class="text-sm font-medium text-brand-500 hover:text-brand-600 dark:text-brand-400 dark:hover:text-brand-300"
          >
            View All
          </router-link>
        </div>

        <div v-if="projectsLoading" class="flex items-center justify-center py-8">
          <svg class="animate-spin h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <div v-else-if="projects.length === 0" class="text-center py-8">
          <div class="flex h-12 w-12 mx-auto items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-800 mb-3">
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">No projects yet</p>
          <router-link
            to="/projects"
            class="mt-2 inline-block text-sm font-medium text-brand-500 hover:text-brand-600"
          >
            Create your first project
          </router-link>
        </div>

        <div v-else class="space-y-3">
          <router-link
            v-for="project in projects.slice(0, 5)"
            :key="project.name"
            :to="`/projects/${encodeURIComponent(project.name)}`"
            class="flex items-center justify-between rounded-lg border border-gray-200 p-4 transition hover:border-brand-300 hover:bg-brand-50/50 dark:border-gray-700 dark:hover:border-brand-700 dark:hover:bg-brand-900/10"
          >
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-100 dark:bg-brand-500/10">
                <svg class="w-5 h-5 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-800 dark:text-white/90">{{ project.name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {{ project.stats.total }} features
                </p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="text-right">
                <p class="text-sm font-medium text-gray-800 dark:text-white/90">
                  {{ project.stats.passing }}/{{ project.stats.total }}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">passing</p>
              </div>
              <div class="h-8 w-8 relative">
                <svg class="w-8 h-8 -rotate-90" viewBox="0 0 36 36">
                  <circle
                    cx="18" cy="18" r="14"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    class="text-gray-200 dark:text-gray-700"
                  />
                  <circle
                    cx="18" cy="18" r="14"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    :stroke-dasharray="`${project.stats.percentage * 0.88} 88`"
                    stroke-linecap="round"
                    class="text-success-500"
                  />
                </svg>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Security Settings -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <h3 class="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">Security</h3>

        <!-- MFA Status -->
        <div class="mb-6 flex items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <div class="flex items-center gap-4">
            <div
              :class="[
                'flex h-12 w-12 items-center justify-center rounded-xl',
                mfaEnabled
                  ? 'bg-success-100 dark:bg-success-500/10'
                  : 'bg-gray-100 dark:bg-gray-800'
              ]"
            >
              <svg
                :class="[
                  'w-6 h-6',
                  mfaEnabled ? 'text-success-500' : 'text-gray-500'
                ]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-800 dark:text-white/90">
                Two-Factor Authentication
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ mfaEnabled ? 'Enabled - Your account is protected' : 'Add an extra layer of security to your account' }}
              </p>
            </div>
          </div>
          <button
            v-if="!mfaEnabled"
            @click="showMfaSetup = true"
            class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600"
          >
            Enable
          </button>
          <button
            v-else
            @click="showMfaDisable = true"
            class="rounded-lg border border-error-300 px-4 py-2 text-sm font-medium text-error-600 transition hover:bg-error-50 dark:border-error-700 dark:text-error-400 dark:hover:bg-error-900/20"
          >
            Disable
          </button>
        </div>

        <!-- Change Password -->
        <div class="flex items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <div class="flex items-center gap-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-800">
              <svg
                class="w-6 h-6 text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
                />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-800 dark:text-white/90">Password</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Change your account password
              </p>
            </div>
          </div>
          <button
            @click="showPasswordModal = true"
            class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Change
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <Modal v-if="showEditModal" @close="showEditModal = false">
      <template #body>
        <div
          class="relative w-full max-w-[500px] rounded-3xl bg-white p-6 dark:bg-gray-900"
        >
          <button
            @click="showEditModal = false"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <h4 class="mb-6 text-xl font-semibold text-gray-800 dark:text-white/90">
            Edit Profile
          </h4>

          <form @submit.prevent="handleUpdateProfile" class="space-y-4">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Full Name
              </label>
              <input
                v-model="editForm.full_name"
                type="text"
                placeholder="Enter your full name"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Bio
              </label>
              <textarea
                v-model="editForm.bio"
                rows="3"
                placeholder="Tell us about yourself"
                class="input-field resize-none"
              ></textarea>
            </div>

            <div v-if="editError" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
              {{ editError }}
            </div>

            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="showEditModal = false"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isLoading"
                class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
              >
                {{ isLoading ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>

    <!-- Change Password Modal -->
    <Modal v-if="showPasswordModal" @close="showPasswordModal = false">
      <template #body>
        <div
          class="relative w-full max-w-[500px] rounded-3xl bg-white p-6 dark:bg-gray-900"
        >
          <button
            @click="showPasswordModal = false"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <h4 class="mb-6 text-xl font-semibold text-gray-800 dark:text-white/90">
            Change Password
          </h4>

          <form @submit.prevent="handleChangePassword" class="space-y-4">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Current Password
              </label>
              <input
                v-model="passwordForm.current_password"
                type="password"
                placeholder="Enter current password"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                New Password
              </label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="Enter new password"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Confirm New Password
              </label>
              <input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="Confirm new password"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              />
            </div>

            <div v-if="passwordError" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
              {{ passwordError }}
            </div>

            <div v-if="passwordSuccess" class="rounded-lg bg-success-50 p-3 text-sm text-success-600 dark:bg-success-900/20 dark:text-success-400">
              {{ passwordSuccess }}
            </div>

            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="showPasswordModal = false"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isLoading"
                class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
              >
                {{ isLoading ? 'Changing...' : 'Change Password' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>

    <!-- MFA Setup Modal -->
    <Modal v-if="showMfaSetup" @close="closeMfaSetup">
      <template #body>
        <div
          class="relative w-full max-w-[500px] rounded-3xl bg-white p-6 dark:bg-gray-900"
        >
          <button
            @click="closeMfaSetup"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <h4 class="mb-2 text-xl font-semibold text-gray-800 dark:text-white/90">
            Enable Two-Factor Authentication
          </h4>
          <p class="mb-6 text-sm text-gray-500 dark:text-gray-400">
            Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
          </p>

          <div v-if="mfaSetupData" class="space-y-6">
            <!-- QR Code -->
            <div class="flex justify-center">
              <div class="rounded-lg bg-white p-4">
                <img :src="mfaSetupData.qrCode" alt="MFA QR Code" class="w-48 h-48" />
              </div>
            </div>

            <!-- Secret Key -->
            <div>
              <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
                Or enter this code manually:
              </p>
              <div class="flex items-center gap-2">
                <code class="flex-1 rounded-lg bg-gray-100 px-3 py-2 font-mono text-sm dark:bg-gray-800">
                  {{ mfaSetupData.secret }}
                </code>
                <button
                  @click="copySecret"
                  class="rounded-lg border border-gray-300 p-2 transition hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800"
                >
                  <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Verification Code -->
            <form @submit.prevent="handleEnableMfa" class="space-y-4">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Verification Code
                </label>
                <input
                  v-model="mfaCode"
                  type="text"
                  maxlength="6"
                  placeholder="Enter 6-digit code"
                  class="input-field text-center font-mono text-lg tracking-widest"
                />
              </div>

              <div v-if="mfaError" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
                {{ mfaError }}
              </div>

              <button
                type="submit"
                :disabled="isLoading || mfaCode.length !== 6"
                class="w-full rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
              >
                {{ isLoading ? 'Verifying...' : 'Enable 2FA' }}
              </button>
            </form>
          </div>

          <div v-else class="flex items-center justify-center py-8">
            <svg class="animate-spin h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </div>
      </template>
    </Modal>

    <!-- MFA Disable Modal -->
    <Modal v-if="showMfaDisable" @close="showMfaDisable = false">
      <template #body>
        <div
          class="relative w-full max-w-[400px] rounded-3xl bg-white p-6 dark:bg-gray-900"
        >
          <button
            @click="showMfaDisable = false"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-error-100 dark:bg-error-900/20">
            <svg class="w-6 h-6 text-error-600 dark:text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>

          <h4 class="mb-2 text-xl font-semibold text-gray-800 dark:text-white/90">
            Disable 2FA?
          </h4>
          <p class="mb-6 text-sm text-gray-500 dark:text-gray-400">
            This will remove the extra layer of security from your account. Enter your authentication code to confirm.
          </p>

          <form @submit.prevent="handleDisableMfa" class="space-y-4">
            <div>
              <input
                v-model="mfaDisableCode"
                type="text"
                maxlength="6"
                placeholder="Enter 6-digit code"
                class="input-field text-center font-mono text-lg tracking-widest"
              />
            </div>

            <div v-if="mfaError" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
              {{ mfaError }}
            </div>

            <div class="flex gap-3">
              <button
                type="button"
                @click="showMfaDisable = false"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isLoading || mfaDisableCode.length !== 6"
                class="flex-1 rounded-lg bg-error-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-error-600 disabled:opacity-50"
              >
                {{ isLoading ? 'Disabling...' : 'Disable 2FA' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import Modal from '@/components/profile/Modal.vue'
import { useAuth } from '@/composables/useAuth'
import { projectsAPI, type ProjectSummary } from '@/api/client'

const {
  user,
  username,
  email,
  fullName,
  mfaEnabled,
  isLoading,
  updateProfile,
  changePassword,
  setupMFA,
  enableMFA,
  disableMFA,
  clearError,
} = useAuth()

// Projects
const projects = ref<ProjectSummary[]>([])
const projectsLoading = ref(true)

const fetchProjects = async () => {
  try {
    projectsLoading.value = true
    projects.value = await projectsAPI.list()
  } catch (error) {
    console.error('Failed to fetch projects:', error)
    projects.value = []
  } finally {
    projectsLoading.value = false
  }
}

onMounted(() => {
  fetchProjects()
})

// Computed
const initials = computed(() => {
  const name = fullName.value || username.value || ''
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

// Modals
const showEditModal = ref(false)
const showPasswordModal = ref(false)
const showMfaSetup = ref(false)
const showMfaDisable = ref(false)

// Edit Profile
const editForm = ref({
  full_name: '',
  bio: '',
})
const editError = ref('')

watch(showEditModal, (show) => {
  if (show) {
    editForm.value = {
      full_name: user.value?.full_name || '',
      bio: user.value?.bio || '',
    }
    editError.value = ''
  }
})

const handleUpdateProfile = async () => {
  editError.value = ''
  const success = await updateProfile(editForm.value)
  if (success) {
    showEditModal.value = false
  } else {
    editError.value = 'Failed to update profile'
  }
}

// Change Password
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const passwordError = ref('')
const passwordSuccess = ref('')

watch(showPasswordModal, (show) => {
  if (show) {
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: '',
    }
    passwordError.value = ''
    passwordSuccess.value = ''
  }
})

const handleChangePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'Passwords do not match'
    return
  }

  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = 'Password must be at least 8 characters'
    return
  }

  const success = await changePassword({
    current_password: passwordForm.value.current_password,
    new_password: passwordForm.value.new_password,
  })

  if (success) {
    passwordSuccess.value = 'Password changed successfully'
    setTimeout(() => {
      showPasswordModal.value = false
    }, 1500)
  } else {
    passwordError.value = 'Failed to change password. Check your current password.'
  }
}

// MFA Setup
const mfaSetupData = ref<{ secret: string; qrCode: string } | null>(null)
const mfaCode = ref('')
const mfaDisableCode = ref('')
const mfaError = ref('')

watch(showMfaSetup, async (show) => {
  if (show) {
    mfaCode.value = ''
    mfaError.value = ''
    mfaSetupData.value = null
    const data = await setupMFA()
    if (data) {
      mfaSetupData.value = data
    } else {
      mfaError.value = 'Failed to initialize MFA setup'
    }
  }
})

watch(showMfaDisable, (show) => {
  if (show) {
    mfaDisableCode.value = ''
    mfaError.value = ''
  }
})

const closeMfaSetup = () => {
  showMfaSetup.value = false
  mfaSetupData.value = null
}

const copySecret = () => {
  if (mfaSetupData.value) {
    navigator.clipboard.writeText(mfaSetupData.value.secret)
  }
}

const handleEnableMfa = async () => {
  mfaError.value = ''
  if (!mfaSetupData.value) return

  const success = await enableMFA({
    secret: mfaSetupData.value.secret,
    code: mfaCode.value,
  })

  if (success) {
    showMfaSetup.value = false
    mfaSetupData.value = null
  } else {
    mfaError.value = 'Invalid code. Please try again.'
  }
}

const handleDisableMfa = async () => {
  mfaError.value = ''
  const success = await disableMFA({ code: mfaDisableCode.value })

  if (success) {
    showMfaDisable.value = false
  } else {
    mfaError.value = 'Invalid code. Please try again.'
  }
}
</script>


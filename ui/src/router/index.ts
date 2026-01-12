import { createRouter, createWebHistory } from 'vue-router'
import { getAuthToken } from '@/api/client'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { left: 0, top: 0 }
  },
  routes: [
    // ========================================================================
    // Public Routes (no auth required)
    // ========================================================================
    {
      path: '/',
      name: 'Landing',
      component: () => import('../views/Landing/LandingPage.vue'),
      meta: {
        title: 'Welcome',
        public: true,
        isLanding: true,
      },
    },
    {
      path: '/signin',
      name: 'Signin',
      component: () => import('../views/Auth/Signin.vue'),
      meta: {
        title: 'Sign In',
        public: true,
      },
    },
    {
      path: '/login',
      redirect: '/signin',
    },
    {
      path: '/signup',
      name: 'Signup',
      component: () => import('../views/Auth/Signup.vue'),
      meta: {
        title: 'Sign Up',
        public: true,
      },
    },
    {
      path: '/error-404',
      name: '404 Error',
      component: () => import('../views/Errors/FourZeroFour.vue'),
      meta: {
        title: '404 Error',
        public: true,
      },
    },

    // ========================================================================
    // Protected Routes (auth required)
    // ========================================================================
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: {
        title: 'Dashboard',
      },
    },
    {
      path: '/projects',
      name: 'Projects',
      component: () => import('../views/Projects/ProjectList.vue'),
      meta: {
        title: 'Projects',
      },
    },
    {
      path: '/projects/overview',
      name: 'ProjectsOverview',
      component: () => import('../views/Projects/ProjectsOverview.vue'),
      meta: {
        title: 'Projects Overview',
      },
    },
    {
      path: '/projects/paused',
      name: 'PausedProjects',
      component: () => import('../views/Projects/PausedProjects.vue'),
      meta: {
        title: 'Paused Projects',
      },
    },
    {
      path: '/projects/finished',
      name: 'FinishedProjects',
      component: () => import('../views/Projects/FinishedProjects.vue'),
      meta: {
        title: 'Finished Projects',
      },
    },
    {
      path: '/projects/in-progress',
      name: 'InProgressProjects',
      component: () => import('../views/Projects/InProgressProjects.vue'),
      meta: {
        title: 'In Progress Projects',
      },
    },
    {
      path: '/projects/new',
      name: 'NewProject',
      component: () => import('../views/Projects/NewProject.vue'),
      meta: {
        title: 'Create New Project',
      },
    },
    {
      path: '/projects/:name',
      name: 'ProjectDetail',
      component: () => import('../views/Projects/ProjectDetail.vue'),
      meta: {
        title: 'Project',
      },
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/Profile/UserProfile.vue'),
      meta: {
        title: 'Profile',
      },
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('../views/Profile/Settings.vue'),
      meta: {
        title: 'Settings',
      },
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: () => import('../views/Analytics/AnalyticsDashboard.vue'),
      meta: {
        title: 'Analytics',
      },
    },
    {
      path: '/docs',
      name: 'Documentation',
      component: () => import('../views/Documentation/DocsPage.vue'),
      meta: {
        title: 'Documentation',
        public: true,
      },
    },

    // Catch-all 404
    {
      path: '/:pathMatch(.*)*',
      redirect: '/error-404',
    },
  ],
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  // Update page title
  document.title = `${to.meta.title || 'Dashboard'} | Nexus - Autonomous Coding Platform`

  // Check if route requires auth
  const isPublicRoute = to.meta.public === true
  const isLandingPage = to.meta.isLanding === true
  const isAuthenticated = !!getAuthToken()

  if (!isPublicRoute && !isAuthenticated) {
    // Redirect to landing if not authenticated (instead of signin)
    next({ name: 'Landing' })
  } else if (isAuthenticated && (to.name === 'Signin' || to.name === 'Signup')) {
    // Redirect authenticated users away from auth pages to landing (not dashboard)
    next({ name: 'Landing' })
  } else {
    next()
  }
})

export default router

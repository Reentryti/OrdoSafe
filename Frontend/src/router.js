import { createRouter, createWebHistory } from "vue-router";
import LoginDoctor from "./views/LoginDoctor.vue";
//import DashboardDoctor from "./views/DashboardDoctor.vue";
import { isAuthenticated } from "./services/auth";

// All routes
const routes = [
  { path: "/", redirect: "/login-doctor" }, 
  { path: "/login-doctor", name: "LoginDoctor", component: LoginDoctor },
  //{ path: "/dashboard", name: "Dashboard", component: Dashboard, meta: { requiresAuth: true }},
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const ok = await isAuthenticated();
    if (!ok) {
      return next("/login-doctor");
    }
  }
  next();
});

export default router;

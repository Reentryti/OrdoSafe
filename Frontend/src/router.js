import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/HomePage.vue"),
  },
  // Auth - Doctor
  {
    path: "/login/doctor",
    name: "LoginDoctor",
    component: () => import("@/views/auth/LoginView.vue"),
    props: { role: "doctor" },
  },
  {
    path: "/signup/doctor",
    name: "SignupDoctor",
    component: () => import("@/views/auth/SignupDoctor.vue"),
  },
  // Auth - Pharmacist
  {
    path: "/login/pharmacist",
    name: "LoginPharmacist",
    component: () => import("@/views/auth/LoginView.vue"),
    props: { role: "pharmacist" },
  },
  {
    path: "/signup/pharmacist",
    name: "SignupPharmacist",
    component: () => import("@/views/auth/SignupPharmacist.vue"),
  },
  // 2FA
  {
    path: "/verify-2fa",
    name: "Verify2FA",
    component: () => import("@/views/auth/Verify2FA.vue"),
  },
  {
    path: "/setup-2fa",
    name: "Setup2FA",
    component: () => import("@/views/auth/Setup2FA.vue"),
    meta: { requiresAuth: true },
  },
  // Doctor Dashboard
  {
    path: "/doctor/dashboard",
    name: "DoctorDashboard",
    component: () => import("@/views/doctor/DashboardDoctor.vue"),
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/doctor/ordonnance/create",
    name: "OrdonnanceCreate",
    component: () => import("@/views/doctor/OrdonnanceCreate.vue"),
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/doctor/ordonnance/:id",
    name: "OrdonnanceDetail",
    component: () => import("@/views/doctor/OrdonnanceDetail.vue"),
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/doctor/ordonnance/:id/edit",
    name: "OrdonnanceEdit",
    component: () => import("@/views/doctor/OrdonnanceEdit.vue"),
    meta: { requiresAuth: true, role: "doctor" },
  },
  // Pharmacist Dashboard
  {
    path: "/pharmacist/dashboard",
    name: "PharmacistDashboard",
    component: () => import("@/views/pharmacist/DashboardPharmacist.vue"),
    meta: { requiresAuth: true, role: "pharmacist" },
  },
  {
    path: "/pharmacist/ordonnance/:id",
    name: "PharmacistOrdonnanceDetail",
    component: () => import("@/views/pharmacist/OrdonnanceDetailPharmacist.vue"),
    meta: { requiresAuth: true, role: "pharmacist" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const { useAuthStore } = await import("@/stores/auth");
    const { state, init } = useAuthStore();

    if (!state.initialized) {
      await init();
    }

    if (!state.user) {
      return next("/");
    }

    if (to.meta.role && state.user.role !== to.meta.role) {
      return next(`/${state.user.role}/dashboard`);
    }
  }
  next();
});

export default router;

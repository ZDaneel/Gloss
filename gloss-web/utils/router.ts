import type { Router } from 'vue-router';

let router: Router | null = null;

export function setRouter(newRouter: Router) {
  router = newRouter;
}

export function getRouter(): Router | null {
  return router;
}

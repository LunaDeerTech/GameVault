import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null);
  const user = ref<any | null>(null);

  function setToken(newToken: string) {
    token.value = newToken;
    // TODO: Store token using electron-store
  }

  function setUser(newUser: any) {
    user.value = newUser;
  }

  function logout() {
    token.value = null;
    user.value = null;
    // TODO: Clear token from electron-store
  }

  return {
    token,
    user,
    setToken,
    setUser,
    logout,
  };
});

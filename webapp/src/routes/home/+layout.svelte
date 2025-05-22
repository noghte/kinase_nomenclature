
<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/user';

  let username: string | null = null;

  onMount(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      goto('/');
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        user.set(data.username);
        username = data.username;
      } else {
        localStorage.removeItem('token');
        user.set(null);
        goto('/');
      }
    } catch {
      localStorage.removeItem('token');
      user.set(null);
      goto('/');
    }
  });

  function logout() {
    localStorage.removeItem('token');
    user.set(null);
    goto('/');
  }
</script>

<div class="flex flex-col min-h-screen">
  <header class="bg-blue-600 text-white p-4 flex justify-between items-center">
    <h1 class="text-lg font-semibold">Kinase Nomenclature Proposals</h1>
    {#if username}
      <div class="flex items-center space-x-4">
        <span>Welcome, {username}</span>
        <button on:click={logout} class="px-3 py-1 bg-red-500 rounded hover:bg-red-600">
          Logout
        </button>
      </div>
    {/if}
  </header>

  <main class="flex-grow container mx-auto px-4 py-8">
    <slot />
  </main>

  <footer class="bg-gray-200 text-gray-700 p-4 text-center">
    <p class="text-sm">Maintained by <a href="https://esbg.bmb.uga.edu">Kannan lab</a> </p>
  </footer>
</div>
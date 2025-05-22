<script lang="ts">
  import { goto } from '$app/navigation';
  import { user } from '$lib/user';

  let username = '';
  let password = '';
  let errorMessage: string | null = null;

  async function handleSubmit() {
    // reset any existing error
    errorMessage = null;
    try {
      const res = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) {
        // server error
        errorMessage = 'Error connecting to server';
        return;
      }
      const data = await res.json();
      if (data.status === 'OK' && data.token) {
        // store JWT and navigate to home page
        localStorage.setItem('token', data.token);
        user.set(username);
        goto('/home');
      } else if (data.status === 'Invalid credentials') {
        // bad credentials
        errorMessage = 'Invalid username or password';
      } else {
        // other application error
        errorMessage = 'Login failed';
      }
    } catch (err) {
      // network or unexpected error
      errorMessage = 'Error connecting to server';
    }
  }
</script>

<div class="flex flex-col min-h-screen">
  <header class="bg-blue-600 text-white p-4 text-center">
    <h1 class="text-lg font-semibold">Kinase Nomenclature Proposals</h1>
  </header>

  <main class="flex-grow flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            id="username"
            type="text"
            bind:value={username}
            required
            class="block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            id="password"
            type="password"
            bind:value={password}
            required
            class="block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>
        <button
          type="submit"
          class="w-full py-3 px-4 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Login
        </button>
      </form>
      {#if errorMessage}
        <p class="mt-4 text-sm text-red-600 text-center">{errorMessage}</p>
      {/if}
    </div>
  </main>

  <footer class="bg-gray-200 text-gray-700 p-4 text-center">
        <p class="text-sm">Maintained by <a href="https://esbg.bmb.uga.edu">Kannan lab</a> </p>
  </footer>
</div>

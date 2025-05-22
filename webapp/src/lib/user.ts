import { writable } from 'svelte/store';

// Store to keep track of authenticated username (null if not authenticated)
export const user = writable<string | null>(null);
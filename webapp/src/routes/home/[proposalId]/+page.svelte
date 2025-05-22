<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/user';
  import { marked } from 'marked';
  export let data: { proposalId: number };

  interface Proposal {
    id: number;
    title: string;
    document_markdown: string;
  }

  let proposal: Proposal | null = null;
  let review: any = null;
  // Parsed HTML content from markdown
  let htmlContent: string = '';
  // Review form fields
  let completeness = 3;
  let factual_accuracy = 3;
  let specificity = 3;
  let coherence = 3;
  let structure = 3;
  let usability = 3;
  let strengths = '';
  let weaknesses = '';
  let suggestions = '';
  let errorMessage: string | null = null;
  let successMessage: string | null = null;

  onMount(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      goto('/');
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/proposals/${data.proposalId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        proposal = json.proposal;
        review = json.review;
        if (review) {
          completeness = review.completeness;
          factual_accuracy = review.factual_accuracy;
          specificity = review.specificity;
          coherence = review.coherence;
          structure = review.structure;
          usability = review.usability;
          strengths = review.strengths;
          weaknesses = review.weaknesses;
          suggestions = review.suggestions;
        }
        // parse markdown to HTML whenever proposal is loaded (convert literal "\\n" to real newlines and enable line breaks)
        const raw = json.proposal.document_markdown.replace(/\\n/g, '\n');
        htmlContent = await marked.parse(raw, { breaks: true });
      } else if (res.status === 401) {
        localStorage.removeItem('token');
        user.set(null);
        goto('/');
      } else {
        errorMessage = 'Could not fetch proposal';
      }
    } catch {
      errorMessage = 'Network error';
    }
  });

  async function submitReview() {
    errorMessage = null;
    successMessage = null;
    const token = localStorage.getItem('token');
    if (!token) {
      goto('/');
      return;
    }
    const payload = {
      completeness,
      factual_accuracy,
      specificity,
      coherence,
      structure,
      usability,
      strengths,
      weaknesses,
      suggestions
    };
    try {
      const res = await fetch(`http://localhost:8000/proposals/${data.proposalId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        successMessage = 'Review submitted successfully';
      } else if (res.status === 401) {
        localStorage.removeItem('token');
        user.set(null);
        goto('/');
      } else {
        const j = await res.json();
        errorMessage = j.detail || 'Could not submit review';
      }
    } catch {
      errorMessage = 'Network error';
    }
  }
</script>

{#if errorMessage}
  <p class="text-red-600 text-center my-4">{errorMessage}</p>
{:else if proposal}
  <div class="prose max-w-none mb-6">
    <h2 class="text-2xl font-semibold mb-4">{proposal.title}</h2>
    <div>{@html htmlContent}</div>
  </div>

  <div class="max-w-2xl mx-auto bg-white shadow rounded-lg p-6 space-y-6">
    <h3 class="text-xl font-semibold">Your Review</h3>
    <div class="grid grid-cols-2 gap-4">
      <label class="block">
        <span>Completeness (1-5)</span>
        <input type="number" min="1" max="5" bind:value={completeness} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" />
      </label>
      <label class="block">
        <span>Factual Accuracy (1-5)</span>
        <input type="number" min="1" max="5" bind:value={factual_accuracy} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" />
      </label>
      <label class="block">
        <span>Specificity (1-5)</span>
        <input type="number" min="1" max="5" bind:value={specificity} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" />
      </label>
      <label class="block">
        <span>Coherence (1-5)</span>
        <input type="number" min="1" max="5" bind:value={coherence} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" />
      </label>
      <label class="block">
        <span>Structure (1-5)</span>
        <input type="number" min="1" max="5" bind:value={structure} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" />
      </label>
      <label class="block">
        <span>Usability (1-5)</span>
        <input type="number" min="1" max="5" bind:value={usability} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" />
      </label>
    </div>
    <label class="block">
      <span>Strengths</span>
      <textarea bind:value={strengths} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" rows="3"></textarea>
    </label>
    <label class="block">
      <span>Weaknesses</span>
      <textarea bind:value={weaknesses} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" rows="3"></textarea>
    </label>
    <label class="block">
      <span>Suggestions</span>
      <textarea bind:value={suggestions} class="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50" rows="3"></textarea>
    </label>
    <button on:click={submitReview} class="mt-4 inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring focus:ring-green-200">
      Submit Review
    </button>
    {#if successMessage}
      <p class="text-green-600 mt-2">{successMessage}</p>
    {/if}
  </div>
{:else}
  <p class="text-center">Loading...</p>
{/if}
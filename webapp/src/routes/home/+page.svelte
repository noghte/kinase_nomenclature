<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/user';
import { AgGrid as AgGridSvelte } from 'ag-grid-svelte5-extended';
import { type GridOptions, type Module } from '@ag-grid-community/core';
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

  interface Proposal {
    id: number;
    title: string;
  }

  let proposals: Proposal[] = [];
  let error: string | null = null;
  // AG Grid configuration
  const modules: Module[] = [ClientSideRowModelModule];
  const gridOptions: GridOptions<Proposal> = {
    columnDefs: [
      { headerName: 'ID', field: 'id', sortable: true, filter: true, width: 100 },
      { headerName: 'Title', field: 'title', sortable: true, filter: true, flex: 1 },
      {
        headerName: 'Action',
        field: 'id',
        cellRenderer: (params: any) => {
          const button = document.createElement('button');
          button.textContent = 'Review';
          button.className = 'px-4 py-0 bg-blue-600 text-white rounded hover:bg-blue-700';
          button.addEventListener('click', (e: any) => { e.stopPropagation(); review(params.value); });
          return button;
        }
      }
    ],
    defaultColDef: { sortable: true, filter: true },
    getRowId: params => params.data.id.toString()
  };

  onMount(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      goto('/');
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/proposals', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        proposals = data.proposals;
      } else if (res.status === 401) {
        localStorage.removeItem('token');
        user.set(null);
        goto('/');
      } else {
        error = 'Could not fetch proposals';
      }
    } catch {
      error = 'Network error';
    }
  });

  function review(id: number) {
    goto(`/home/${id}`);
  }
</script>

{#if error}
  <p class="text-red-600 text-center mt-4">{error}</p>
{:else}
  <AgGridSvelte
    {gridOptions}
    rowData={proposals}
    {modules}
    gridClass="ag-theme-alpine mx-4"
    gridStyle="height: 500px; width: calc(100% - 2rem);"
    sizeColumnsToFit={true}
  />
{/if}
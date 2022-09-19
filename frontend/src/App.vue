<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Service } from "@/service";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { FilterMatchMode } from "primevue/api";
import InputText from "primevue/inputtext";
import TabPanel from "primevue/tabpanel";
import TabView from "primevue/tabview";

const shows = ref();
const movies = ref();
const webcomics = ref();
const activeTab = ref(0);
const service = new Service();

const multiSortMeta = ref([
  { field: "status", order: 1 },
  { field: "name", order: 1 }
]);

const filters = ref({
  "name": { value: null, matchMode: FilterMatchMode.CONTAINS }
});

const updateData = () => {
  switch (activeTab.value) {
    case 0:
      service.getShow().then(data => {
        shows.value = data;
      });
      break;
    case 1:
      service.getMovie().then(data => {
        movies.value = data;
      });
      break;
    case 2:
      service.getWebcomic().then(data => {
        webcomics.value = data;
        console.log(data);
      });
      break;
  }
};

const onCellEditComplete = (event) => {
  let { data, newValue, field } = event;

  data[field] = newValue;
}

onMounted(() => {
  updateData();
});

</script>

<template>
  <TabView class="m-3" v-model:activeIndex="activeTab" @tab-change="updateData">
    <TabPanel header="Shows" class="min-h-screen">
          <DataTable :value="shows" sortMode="multiple" :multiSortMeta="multiSortMeta" :scrollable="true" scrollHeight="400px" v-model:filters="filters"
                     filterDisplay="row" editMode="cell" @cell-edit-complete="onCellEditComplete">
            <template #header>
                  <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText v-model="filters['name'].value" placeholder="Keyword Search" />
                  </span>
            </template>
            <Column field="name" header="Name" :sortable="true">
              <template #editor="{ data, field }">
                <InputText v-model="data[field]" autofocus />
              </template>
            </Column>
            <Column field="season" header="Season" :sortable="true" />
            <Column field="episode" header="Episode" :sortable="true" />
            <Column field="status" header="Status" :sortable="true" />
            <Column field="date_started" header="Date Started" :sortable="true" />
            <Column field="date_finished" header="Date Finished" :sortable="true" />
            <Column field="last_updated" header="Last Updated" :sortable="true" />
          </DataTable>
    </TabPanel>
    <TabPanel header="Movies">
      <DataTable :value="movies">
        <Column field="name" header="Name" :sortable="true" />
        <Column field="status" header="Status" :sortable="true" />
        <Column field="date_watched" header="Date Watched" :sortable="true" />
        <Column field="last_updated" header="Last Updated" :sortable="true" />
      </DataTable>
    </TabPanel>
    <TabPanel header="Webcomics">
      <DataTable :value="webcomics">
        <Column field="name" header="Name" :sortable="true" />
        <Column field="last_updated" header="Last Updated" :sortable="true" />
      </DataTable>
    </TabPanel>
  </TabView>
</template>

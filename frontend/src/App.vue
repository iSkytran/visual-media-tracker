<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Service } from "@/service";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import TabPanel from "primevue/tabpanel";
import TabView from "primevue/tabview";

const shows = ref();
const movies = ref();
const webcomics = ref();
const activeTab = ref(0);
const service = new Service();

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
        console.log(data)
      });
      break;
  }
};

onMounted(() => {
  updateData()
});

</script>

<template>
  <TabView class="m-3" v-model:activeIndex="activeTab" @tab-change="updateData">
    <TabPanel header="Shows">
      <DataTable :value="shows">
        <Column field="name" header="Name" />
        <Column field="season" header="Season" />
        <Column field="episode" header="Episode" />
        <Column field="date_started" header="Date Started" />
        <Column field="date_finished" header="Date Finished" />
        <Column field="last_updated" header="Last Updated" />
      </DataTable>
    </TabPanel>
    <TabPanel header="Movies">
      <DataTable :value="movies">
        <Column field="name" header="Name" />
        <Column field="date_watched" header="Date Watched" />
        <Column field="last_updated" header="Last Updated" />
      </DataTable>
    </TabPanel>
    <TabPanel header="Webcomics">
      <DataTable :value="webcomics">
        <Column field="name" header="Name" />
        <Column field="last_updated" header="Last Updated" />
      </DataTable>
    </TabPanel>
  </TabView>
</template>

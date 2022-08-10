<template>
  <div class="container q-mt-lg hnhead">
    <div class="q-my-xl text-center block">
      <h1 class="q-mb-none">Classic HN</h1>
      <h4 class="q-mt-none">Find value in old wisdom</h4>
      <p class="text-subtitle1">A database of all articles in <a href="https://news.ycombinator.com">Hacker News</a> that include a
      (year) in the title and received over 100 points</p>
      <p class="text-subtitle2">From 1950 to 2015</p>
    </div>
    <div class="row items-center justify-evenly full-width q-gutter-md q-my-lg">
      <q-input v-model="query" label="Search" class="col-grow" outlined/>
      <q-select v-model="year" label="Year" :options="years" option-label="label" option-value="value" emit-value map-options class="col-grow" outlined/>
      <q-separator/>
    </div>
    <q-table
      flat
      title="Articles"
      :rows="documents"
      :columns="columns"
      row-key="id"
      :rows-per-page-options="[20, 50, 100, 200, 500, 1000]"
      class="container q-pb-lg"
    >
      <template v-slot:body-cell-comments="{ row }">
        <q-td class="text-center">
          <a :href="`https://news.ycombinator.com/item?id=${row.id}`" target="_blank">
            {{ row.comments }}
          </a>
        </q-td>
      </template>
      <template v-slot:body-cell-url="{ row }">
        <q-td class="text-right">
          <q-btn
            flat
            round
            dense
            icon="link"
            type="a"
            :href="row.url"
            target="_blank"
          />
        </q-td>
      </template>
    </q-table>
  </div>
  <div class="text-center q-pa-xl container footer">
    <p>Built by <a href="https://prealfa.com">Adrià</a> in <a href="https://en.wikipedia.org/wiki/Valencia">València</a> with 🥘 and ❤️</p>
    <p><a href="https://github.com/adlpz/classics.rtf.cc/">Check out the source code</a></p>
    <p>Download this database in <a href="https://github.com/adlpz/classics.rtf.cc/raw/master/articles.json">JSON</a> or <a href="https://github.com/adlpz/classics.rtf.cc/raw/master/articles.db">Sqlite</a></p>
    <p>If you use this code or dataset <a href="https://twitter.com/adlpz">say hi on Twitter</a>.</p>
  </div>

</template>

<script lang="ts" setup>

import {computed, inject, ref, watch} from "vue";
import {Index} from "flexsearch";

const columns = [
  {name: 'title', align: 'left', label: 'Title', field: 'title', sortable: true},
  {name: 'year', align: 'left', label: 'Year', field: 'year', sortable: true},
  {name: 'author', align: 'left', label: 'Submitted by', field: 'author', sortable: true},
  {name: 'points', align: 'center', label: 'Points', field: 'points', sortable: true},
  {name: 'comments', align: 'center', label: 'Comments', field: 'comments', sortable: true},
  {name: 'url', align: 'right', label: 'Link', field: 'url', sortable: true},
]

const index = inject<Index>('index');
const get = inject('get')
const data = inject('data')
const loading = ref(false);
const query = ref('')
const year = ref<number | null>(null)
const years = [...Array(66)].map((d, i) => i + 1950).reduce((acc, cur) => {
  acc.push({label: cur, value: cur})
  return acc
}, [{label: 'All years', value: null}])
const matches = ref(data)
const documents = computed(() => matches.value.filter(article => year.value ? article.year === year.value : true).sort((a, b) => b.points - a.points))
watch(query, (value) => {
  if (!value) {
    matches.value = data
    return
  }

  loading.value = true
  matches.value = index.search(query.value).map(index => get(index))
  loading.value = false
})
</script>

<style scoped>
.container {
  max-width: 960px;
  margin: 0 auto;
}
.hnhead {
  border-top: 20px solid rgb(255, 102, 0);
}
.footer {
  border-top: 4px solid rgb(255, 102, 0);
}
</style>

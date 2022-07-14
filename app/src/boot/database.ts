import { boot } from 'quasar/wrappers'
import data from '../../../articles.json'
import {Index} from 'flexsearch'

// "async" is optional;
// more info on params: https://v2.quasar.dev/quasar-cli/boot-files
export default boot(async ({ app }) => {
  const index = new Index({preset: 'match', tokenize: 'full'})
  for (let i = 0; i < data.length; i++) {
    index.add(i, data[i].title)
  }

  app.provide('data', data)
  app.provide('index', index)
  app.provide('get', (index: number) => data[index])
})

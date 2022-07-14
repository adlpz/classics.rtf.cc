import { PromisedDatabase } from 'promised-sqlite3'
import fs from 'fs'
import glob from 'glob'
import { Readability, isProbablyReaderable } from '@mozilla/readability'
import { JSDOM } from 'jsdom'
import fetch from 'node-fetch'
import * as url from 'url';


const __dirname = url.fileURLToPath(new URL('.', import.meta.url));

const db = new PromisedDatabase()
const out = __dirname + '/../articles/'

async function execute() {
    await db.open(__dirname + '/../articles.db')

    const items = await db.all('SELECT id, url FROM articles')
    await db.close()

    console.log(`Fetched ${items.length} items from the DB`)

    await Promise.all(items.map(({id, url}) => get(id, url)))
}

async function get(id, url) {
    const rid = id.toString().padStart(10, '0')

    if (glob.sync(out + id + '.*').length) {
        console.log(`${rid} : Skipped`)
            return
    }

    console.log(`${rid} : Fetching...`)
    const result = await fetch(url)
    console.log(`${rid} : Received!`)
    const body = await result.text()
    const type = result.headers.get('Content-Type')
    if (!type.toLowerCase().includes('html')) {
        // treat this as a binary
        fs.writeFileSync(out + id + '.bin', body)
        console.log(`${rid} : Binary stored`)
        return
    }

    // This is a HTML. Fetch readable version.
    const doc = (new JSDOM(body, { url }))?.window?.document

    if (!isProbablyReaderable(doc)) {
        // Not readerable. Store whatever we downloaded as 'raw'
        fs.writeFileSync(out + id + '.html', body)
        console.log(`${rid} : Is HTML but cannot make readable. Storing raw.`)
        return
    }

    const reader = new Readability(doc)
    const parsed = reader.parse()
    fs.writeFileSync(out + id + '.html', parsed.content)
    console.log(`${rid} : Readable version stored`)
}


execute()






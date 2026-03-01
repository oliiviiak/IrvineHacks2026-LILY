export type DocumentCollection = {
    name: string,
    date: Date,
    documents: Document[]
    alert_count: number
}

export type Document = {
    overview: string,
    content: string,
    url: string
}

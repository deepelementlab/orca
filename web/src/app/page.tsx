import ResearchPanel from '@/components/research-panel/ResearchPanel'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight">
            <span className="text-orca-500">Orca</span>
          </h1>
          <p className="mt-2 text-gray-400">
            Omniscient Research Companion & Assistant
          </p>
        </header>
        <ResearchPanel />
      </div>
    </main>
  )
}

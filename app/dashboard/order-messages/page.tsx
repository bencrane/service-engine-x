import Link from "next/link";

export default function OrderMessagesPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border px-8 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-muted-foreground hover:text-foreground">
              Dashboard
            </Link>
            <span className="text-muted-foreground/50">/</span>
            <h1 className="text-xl font-semibold">OrderMessages</h1>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-8">
        <p className="text-muted-foreground">Coming soon.</p>
      </div>
    </main>
  );
}

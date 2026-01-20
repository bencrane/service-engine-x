import { redirect } from "next/navigation";
import Link from "next/link";
import { getSession } from "@/lib/auth";

export default async function ClientsPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login");
  }

  return (
    <main className="min-h-screen bg-black text-white">
      <header className="border-b border-gray-800 px-8 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-400 hover:text-white">
              Dashboard
            </Link>
            <span className="text-gray-600">/</span>
            <h1 className="text-xl font-semibold">Clients</h1>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-8">
        <p className="text-gray-400">Client list coming soon.</p>
      </div>
    </main>
  );
}

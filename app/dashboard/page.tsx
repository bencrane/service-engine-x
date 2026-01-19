import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth";
import { LogoutButton } from "./logout-button";

export default async function DashboardPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login");
  }

  return (
    <main className="min-h-screen bg-black p-8">
      <div className="max-w-2xl mx-auto bg-white p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <LogoutButton />
        </div>
        <p className="text-gray-600">Logged in as {session.users.email}</p>
      </div>
    </main>
  );
}

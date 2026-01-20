import { redirect } from "next/navigation";
import Link from "next/link";
import { getSession } from "@/lib/auth";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export default async function ClientsPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login");
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border px-8 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-muted-foreground hover:text-foreground">
              Dashboard
            </Link>
            <span className="text-muted-foreground/50">/</span>
            <h1 className="text-xl font-semibold">Clients</h1>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <Link href="/dashboard/clients/create" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Create a Client</CardTitle>
                <CardDescription>Add a new client to your system</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/clients/view" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>View Client Details</CardTitle>
                <CardDescription>View client information</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/clients/edit" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Edit Client</CardTitle>
                <CardDescription>Update client information</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/clients/delete" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Delete Client</CardTitle>
                <CardDescription>Remove a client from the system</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        </div>
      </div>
    </main>
  );
}

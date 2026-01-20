import { redirect } from "next/navigation";
import Link from "next/link";
import { getSession } from "@/lib/auth";
import { LogoutButton } from "./logout-button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export default async function DashboardPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login");
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border px-8 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {session.users.email}
            </span>
            <LogoutButton />
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link href="/dashboard/clients" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Clients</CardTitle>
                <CardDescription>Manage your clients</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/tasks" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Tasks</CardTitle>
                <CardDescription>Manage tasks</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/coupons" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Coupons</CardTitle>
                <CardDescription>Manage coupons</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/filled-form-fields" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>FilledFormFields</CardTitle>
                <CardDescription>Manage filled form fields</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/invoices" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Invoices</CardTitle>
                <CardDescription>Manage invoices</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/logs" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Logs</CardTitle>
                <CardDescription>View system logs</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/magic-link" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>MagicLink</CardTitle>
                <CardDescription>Manage magic links</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/orders" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Orders</CardTitle>
                <CardDescription>Manage orders</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/order-messages" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>OrderMessages</CardTitle>
                <CardDescription>Manage order messages</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/order-tasks" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>OrderTasks</CardTitle>
                <CardDescription>Manage order tasks</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/services" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Services</CardTitle>
                <CardDescription>Manage services</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/subscriptions" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Subscriptions</CardTitle>
                <CardDescription>Manage subscriptions</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/tags" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Tags</CardTitle>
                <CardDescription>Manage tags</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/team" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Team</CardTitle>
                <CardDescription>Manage team members</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/tickets" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Tickets</CardTitle>
                <CardDescription>Manage tickets</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/ticket-messages" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>TicketMessages</CardTitle>
                <CardDescription>Manage ticket messages</CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/dashboard/client-activities" className="block">
            <Card className="hover:border-muted-foreground transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>ClientActivities</CardTitle>
                <CardDescription>Manage client activities</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        </div>
      </div>
    </main>
  );
}

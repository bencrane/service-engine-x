import { cookies } from "next/headers";
import { supabase } from "./supabase";
import bcrypt from "bcryptjs";
import { randomBytes } from "crypto";

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

export async function createSession(userId: string): Promise<string> {
  const token = randomBytes(32).toString("hex");
  const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

  await supabase.from("sessions").insert({
    user_id: userId,
    token,
    expires_at: expiresAt.toISOString(),
  });

  const cookieStore = await cookies();
  cookieStore.set("session", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    expires: expiresAt,
    path: "/",
  });

  return token;
}

export async function getSession() {
  const cookieStore = await cookies();
  const token = cookieStore.get("session")?.value;

  if (!token) return null;

  const { data: session } = await supabase
    .from("sessions")
    .select("*, users(*)")
    .eq("token", token)
    .gt("expires_at", new Date().toISOString())
    .single();

  return session;
}

export async function destroySession() {
  const cookieStore = await cookies();
  const token = cookieStore.get("session")?.value;

  if (token) {
    await supabase.from("sessions").delete().eq("token", token);
    cookieStore.delete("session");
  }
}

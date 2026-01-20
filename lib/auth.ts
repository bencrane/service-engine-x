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

// ============================================
// API Token Authentication
// ============================================

export interface ApiAuthResult {
  valid: boolean;
  userId: string | null;
  error?: string;
}

/**
 * Validates a Bearer token against the api_tokens table.
 * Returns the associated user_id if valid.
 */
export async function validateApiToken(token: string): Promise<ApiAuthResult> {
  if (!token) {
    return { valid: false, userId: null, error: "No token provided" };
  }

  // Hash the token to compare against stored hash
  const encoder = new TextEncoder();
  const data = encoder.encode(token);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const tokenHash = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

  // Look up the token in the database
  const { data: tokenRecord, error } = await supabase
    .from("api_tokens")
    .select("id, user_id, expires_at")
    .eq("token_hash", tokenHash)
    .single();

  if (error || !tokenRecord) {
    return { valid: false, userId: null, error: "Invalid token" };
  }

  // Check if token is expired
  if (tokenRecord.expires_at && new Date(tokenRecord.expires_at) < new Date()) {
    return { valid: false, userId: null, error: "Token expired" };
  }

  // Update last_used_at
  await supabase
    .from("api_tokens")
    .update({ last_used_at: new Date().toISOString() })
    .eq("id", tokenRecord.id);

  return { valid: true, userId: tokenRecord.user_id };
}

/**
 * Extracts Bearer token from Authorization header
 */
export function extractBearerToken(authHeader: string | null): string | null {
  if (!authHeader?.startsWith("Bearer ")) {
    return null;
  }
  return authHeader.slice(7);
}

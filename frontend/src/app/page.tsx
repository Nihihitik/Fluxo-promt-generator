"use client";

import { Button } from "@/components/ui/button";
import { User } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { UserProfile } from "@/components/user-profile";
import { PromptGenerator } from "@/components/prompt-generator";
import { useAuth } from "@/context/auth-context";
import Link from "next/link";

export default function Home() {
  const { user, loading } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-foreground">Fluxo</h1>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            {loading ? (
              <div className="h-10 w-10 rounded-full bg-muted animate-pulse" />
            ) : user ? (
              <UserProfile />
            ) : (
              <Button variant="outline" size="sm" asChild>
                <Link href="/login">
                  <User className="h-4 w-4 mr-2" />
                  Войти
                </Link>
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <PromptGenerator />
      </main>
    </div>
  );
}

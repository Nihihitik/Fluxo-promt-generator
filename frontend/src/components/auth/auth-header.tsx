import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";

export function AuthHeader() {
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="text-2xl font-bold text-foreground">
          Fluxo
        </Link>
        <ThemeToggle />
      </div>
    </header>
  );
}
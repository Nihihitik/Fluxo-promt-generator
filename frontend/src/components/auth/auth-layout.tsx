import { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { AuthHeader } from "./auth-header";

interface AuthLayoutProps {
  children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <AuthHeader />
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md space-y-4">
          {children}
          <div className="pt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push('/')}
              className="w-full"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Вернуться на главную
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
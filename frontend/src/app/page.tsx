import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { User, Send } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-foreground">Fluxo</h1>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Button variant="outline" size="sm" asChild>
              <Link href="/auth">
                <User className="h-4 w-4 mr-2" />
                Войти
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight mb-4">
              Создавайте с помощью ИИ
            </h2>
            <p className="text-muted-foreground text-lg">
              Введите ваш запрос и получите мгновенный результат
            </p>
          </div>

          <div className="flex gap-2">
            <Input
              placeholder="Введите ваш промпт..."
              className="flex-1"
            />
            <Button size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>О проекте</CardTitle>
                <CardDescription>
                  Узнайте больше о возможностях Fluxo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Fluxo - это современная платформа для работы с искусственным интеллектом, 
                  которая предоставляет простой и интуитивный интерфейс для создания контента.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Возможности</CardTitle>
                <CardDescription>
                  Что вы можете делать с Fluxo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li>• Генерация текста и контента</li>
                  <li>• Анализ и обработка данных</li>
                  <li>• Создание креативных решений</li>
                  <li>• Автоматизация рабочих процессов</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PromptStyleSelector } from "@/components/prompt-style-selector";
import { PromptResult } from "@/components/prompt-result";
import { useAuth } from "@/context/auth-context";
import { apiClient } from "@/lib/api";
import { Send, Sparkles, AlertTriangle } from "lucide-react";
import Link from "next/link";

const PROMPT_STYLES = [
  { id: 1, name: "Профессиональный" },
  { id: 2, name: "Творческий" },
  { id: 3, name: "Аналитический" },
  { id: 4, name: "Простой" }
];

export function PromptGenerator() {
  const { user, token } = useAuth();
  const [prompt, setPrompt] = useState("");
  const [selectedStyleId, setSelectedStyleId] = useState<number | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('🔐 Состояние авторизации:', {
      user: user ? {
        id: user.id,
        email: user.email,
        is_email_confirmed: user.is_email_confirmed
      } : null,
      token: token ? `${token.substring(0, 10)}...` : null,
      tokenLength: token?.length || 0
    });
    
    if (!user || !token) {
      setError("Необходимо войти в систему для генерации промптов");
      return;
    }

    if (!prompt.trim()) {
      setError("Введите текст промпта");
      return;
    }

    if (prompt.trim().length > 1000) {
      setError("Промпт слишком длинный (максимум 1000 символов)");
      return;
    }

    if (!selectedStyleId) {
      setError("Выберите стиль генерации");
      return;
    }

    if (selectedStyleId < 1 || selectedStyleId > 4) {
      setError("Выберите корректный стиль (1-4)");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiClient.createPrompt(prompt.trim(), selectedStyleId, token);
      setResult(response.generated_prompt);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Произошла ошибка при генерации промпта");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    handleSubmit(new Event('submit') as any);
  };

  const handleReset = () => {
    setPrompt("");
    setSelectedStyleId(null);
    setResult(null);
    setError(null);
  };

  const selectedStyle = selectedStyleId 
    ? PROMPT_STYLES.find(style => style.id === selectedStyleId)
    : undefined;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Заголовок */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight">
            Генератор промптов
          </h1>
        </div>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          Введите ваш запрос, выберите стиль генерации и получите оптимизированный ответ от ИИ
        </p>
      </div>

      {/* Проверка авторизации */}
      {!user && (
        <Card className="border-amber-200 bg-amber-50 dark:bg-amber-900/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
              <div>
                <p className="text-amber-800 dark:text-amber-200 font-medium">
                  Требуется авторизация
                </p>
                <p className="text-amber-700 dark:text-amber-300 text-sm mt-1">
                  Для использования генератора промптов необходимо войти в систему.
                </p>
                <Button asChild className="mt-3" size="sm">
                  <Link href="/auth">
                    Войти в систему
                  </Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Основная форма */}
      <Card>
        <CardHeader>
          <CardTitle>Создание промпта</CardTitle>
          <CardDescription>
            Опишите ваш запрос и выберите подходящий стиль для генерации
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Ввод промпта */}
            <div className="space-y-2">
              <Label htmlFor="prompt">Ваш запрос</Label>
              <Input
                id="prompt"
                placeholder="Например: Объясни принципы работы квантовых компьютеров"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="min-h-[60px] resize-none"
                disabled={!user || isLoading}
                maxLength={1000}
              />
              <div className="flex justify-between items-center">
                <p className="text-xs text-muted-foreground">
                  Опишите максимально подробно, что именно вы хотите получить
                </p>
                <p className="text-xs text-muted-foreground">
                  {prompt.length}/1000
                </p>
              </div>
            </div>

            {/* Выбор стиля */}
            <div className="space-y-4">
              <Label>Стиль генерации</Label>
              <PromptStyleSelector
                selectedStyleId={selectedStyleId}
                onStyleSelect={setSelectedStyleId}
                disabled={!user || isLoading}
              />
            </div>

            {/* Кнопки управления */}
            <div className="flex items-center gap-3 pt-4">
              <Button 
                type="submit" 
                disabled={!user || !prompt.trim() || !selectedStyleId || isLoading}
                className="gap-2"
              >
                {isLoading ? (
                  <>
                    <Sparkles className="h-4 w-4 animate-pulse" />
                    Генерируем...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Сгенерировать
                  </>
                )}
              </Button>
              
              {(result || error) && (
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleReset}
                  disabled={isLoading}
                >
                  Создать новый
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Результат */}
      <PromptResult
        result={result}
        isLoading={isLoading}
        error={error}
        onRetry={handleRetry}
        originalPrompt={prompt}
        selectedStyle={selectedStyle}
      />
    </div>
  );
}
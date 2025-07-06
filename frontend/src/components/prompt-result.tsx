"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Copy,
  Check,
  Loader2,
  Sparkles,
  AlertCircle,
  RefreshCw
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface PromptResultProps {
  result: string | null;
  isLoading: boolean;
  error: string | null;
  onRetry?: () => void;
  originalPrompt?: string;
  selectedStyle?: {
    id: number;
    name: string;
  };
}

export function PromptResult({
  result,
  isLoading,
  error,
  onRetry,
  originalPrompt,
  selectedStyle
}: PromptResultProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!result) return;

    try {
      await navigator.clipboard.writeText(result);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Ошибка копирования:', err);
    }
  };

  // Показываем компонент только если есть результат, загрузка или ошибка
  if (!result && !isLoading && !error) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">
              {isLoading ? "Генерируем ответ..." : error ? "Ошибка генерации" : "Результат"}
            </CardTitle>
          </div>
          {selectedStyle && (
            <Badge variant="secondary">
              {selectedStyle.name}
            </Badge>
          )}
        </div>
        {originalPrompt && (
          <CardDescription className="text-sm">
            <strong>Ваш запрос:</strong> {originalPrompt}
          </CardDescription>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="text-center space-y-3">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="text-sm text-muted-foreground">
                ИИ обрабатывает ваш запрос...
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-3 p-4 border border-red-200 rounded-lg bg-red-50 dark:bg-red-900/20">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-red-700 dark:text-red-300 font-medium">
                Произошла ошибка
              </p>
              <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                {error}
              </p>
              {onRetry && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onRetry}
                  className="mt-3"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Попробовать снова
                </Button>
              )}
            </div>
          </div>
        )}

        {result && !isLoading && (
          <>
            <div className="relative">
              <div className="p-4 bg-card rounded-lg border shadow-sm prose dark:prose-invert max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result}
                </ReactMarkdown>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <p className="text-xs text-muted-foreground">
                Сгенерировано с помощью ИИ • {new Date().toLocaleTimeString('ru-RU')}
              </p>

              <Button
                variant="outline"
                size="sm"
                onClick={handleCopy}
                className="gap-2"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 text-green-500" />
                    Скопировано!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    Копировать
                  </>
                )}
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
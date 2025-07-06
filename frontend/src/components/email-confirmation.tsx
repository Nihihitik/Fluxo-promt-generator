"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api";
import { Mail, RefreshCw, CheckCircle } from "lucide-react";

interface EmailConfirmationProps {
  email: string;
  onConfirmed: () => void;
  onBack: () => void;
}

export function EmailConfirmation({ email, onConfirmed, onBack }: EmailConfirmationProps) {
  const [code, setCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [resendCount, setResendCount] = useState(0);
  const [resendCooldown, setResendCooldown] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (resendCooldown > 0) {
      interval = setInterval(() => {
        setResendCooldown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [resendCooldown]);

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (code.length !== 6) {
      setError("Код должен содержать 6 цифр");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.confirmEmail({ email, code });
      setSuccess(response.message);
      setTimeout(() => {
        onConfirmed();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла ошибка при подтверждении");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCount >= 3) {
      setError("Превышен лимит отправки (3 раза в час). Попробуйте позже.");
      return;
    }

    if (resendCooldown > 0) {
      return;
    }

    setIsResending(true);
    setError(null);

    try {
      const response = await apiClient.resendConfirmation({ email });
      setSuccess("Код отправлен повторно на ваш email");
      setResendCount(prev => prev + 1);
      setResendCooldown(60); // 60 секунд
      setCode(""); // Очистить поле кода
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла ошибка при отправке");
    } finally {
      setIsResending(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
          <Mail className="h-6 w-6 text-blue-600 dark:text-blue-400" />
        </div>
        <CardTitle>Подтвердите ваш email</CardTitle>
        <CardDescription>
          Мы отправили код подтверждения на
          <br />
          <strong>{email}</strong>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="p-3 text-sm text-green-500 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            {success}
          </div>
        )}

        <form onSubmit={handleConfirm} className="space-y-4">
          <div>
            <Label htmlFor="code">Код подтверждения</Label>
            <Input
              id="code"
              type="text"
              placeholder="123456"
              value={code}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                setCode(value);
                setError(null);
              }}
              maxLength={6}
              className="text-center text-lg font-mono"
              autoFocus
            />
            <p className="text-xs text-muted-foreground mt-1">
              Введите 6-значный код из письма
            </p>
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading || code.length !== 6}
          >
            {isLoading ? "Подтверждение..." : "Подтвердить email"}
          </Button>
        </form>

        <div className="text-center space-y-2">
          <p className="text-sm text-muted-foreground">
            Не получили код?
          </p>
          <Button
            variant="ghost"
            onClick={handleResend}
            disabled={isResending || resendCooldown > 0 || resendCount >= 3}
            className="text-sm"
          >
            {isResending ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Отправка...
              </>
            ) : resendCooldown > 0 ? (
              `Повторить через ${formatTime(resendCooldown)}`
            ) : resendCount >= 3 ? (
              "Лимит отправки исчерпан"
            ) : (
              "Отправить код повторно"
            )}
          </Button>
          {resendCount > 0 && resendCount < 3 && (
            <p className="text-xs text-muted-foreground">
              Использовано попыток: {resendCount}/3
            </p>
          )}
        </div>

        <Button
          variant="outline"
          onClick={onBack}
          className="w-full"
        >
          Назад к регистрации
        </Button>
      </CardContent>
    </Card>
  );
}
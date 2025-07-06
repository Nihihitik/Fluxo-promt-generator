"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { apiClient } from "@/lib/api";
import { EmailConfirmation } from "@/components/email-confirmation";
import { AuthLayout } from "@/components/auth/auth-layout";
import { ErrorMessage } from "@/components/auth/error-message";

const registerSchema = z.object({
  email: z.string().email("Введите корректный email"),
  password: z.string().min(6, "Пароль должен содержать минимум 6 символов"),
  name: z.string().min(2, "Имя должно содержать минимум 2 символа"),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState<string>("");
  const router = useRouter();

  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      password: "",
      name: "",
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      await apiClient.register(data);
      setRegisteredEmail(data.email);
      setShowEmailConfirmation(true);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла ошибка при регистрации");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailConfirmed = async () => {
    router.push(`/login?email=${encodeURIComponent(registeredEmail)}`);
  };

  const handleBackToRegister = () => {
    setShowEmailConfirmation(false);
    setError(null);
  };

  return (
    <AuthLayout>
      {showEmailConfirmation ? (
        <EmailConfirmation
          email={registeredEmail}
          onConfirmed={handleEmailConfirmed}
          onBack={handleBackToRegister}
        />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Регистрация</CardTitle>
            <CardDescription>
              Создайте новый аккаунт для начала работы
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && <ErrorMessage message={error} />}

            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Имя</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Ваше имя"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="your@email.com"
                          type="email"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Пароль</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="••••••••"
                          type="password"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? "Создаем аккаунт..." : "Создать аккаунт"}
                </Button>
              </form>
            </Form>

            <div className="text-center">
              <Button
                variant="link"
                asChild
                className="text-sm"
              >
                <Link href="/login">
                  Уже есть аккаунт? Войдите
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </AuthLayout>
  );
}
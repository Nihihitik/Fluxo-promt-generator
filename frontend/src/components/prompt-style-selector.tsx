"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Briefcase, 
  Lightbulb, 
  BarChart3, 
  GraduationCap,
  Check 
} from "lucide-react";

export interface PromptStyle {
  id: number;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const PROMPT_STYLES: PromptStyle[] = [
  {
    id: 1,
    name: "Профессиональный",
    description: "Экспертный подход с точными и компетентными ответами",
    icon: <Briefcase className="h-5 w-5" />,
    color: "bg-blue-500"
  },
  {
    id: 2, 
    name: "Творческий",
    description: "Креативный подход с нестандартными решениями",
    icon: <Lightbulb className="h-5 w-5" />,
    color: "bg-purple-500"
  },
  {
    id: 3,
    name: "Аналитический", 
    description: "Детальный анализ с разбором по пунктам",
    icon: <BarChart3 className="h-5 w-5" />,
    color: "bg-green-500"
  },
  {
    id: 4,
    name: "Простой",
    description: "Понятные объяснения для новичков с примерами",
    icon: <GraduationCap className="h-5 w-5" />,
    color: "bg-orange-500"
  }
];

interface PromptStyleSelectorProps {
  selectedStyleId: number | null;
  onStyleSelect: (styleId: number) => void;
  disabled?: boolean;
}

export function PromptStyleSelector({ 
  selectedStyleId, 
  onStyleSelect, 
  disabled = false 
}: PromptStyleSelectorProps) {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">Выберите стиль генерации</h3>
        <p className="text-sm text-muted-foreground">
          Каждый стиль создает уникальный подход к обработке вашего запроса
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {PROMPT_STYLES.map((style) => {
          const isSelected = selectedStyleId === style.id;
          
          return (
            <Card 
              key={style.id}
              className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                isSelected 
                  ? 'ring-2 ring-primary border-primary/50 bg-primary/5' 
                  : 'hover:border-primary/30'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => !disabled && onStyleSelect(style.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${style.color} text-white`}>
                      {style.icon}
                    </div>
                    <div>
                      <CardTitle className="text-base">{style.name}</CardTitle>
                      {isSelected && (
                        <Badge variant="default" className="mt-1">
                          <Check className="h-3 w-3 mr-1" />
                          Выбран
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <CardDescription className="text-sm">
                  {style.description}
                </CardDescription>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {selectedStyleId && (
        <div className="text-center">
          <Button 
            variant="outline" 
            onClick={() => onStyleSelect(null as any)}
            disabled={disabled}
            size="sm"
          >
            Сбросить выбор
          </Button>
        </div>
      )}
    </div>
  );
}